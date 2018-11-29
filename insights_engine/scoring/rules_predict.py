"""Contains the ScoringEngine used for predictions."""
import os

import pandas as pd

import insights_engine.config as config
from insights_engine.data_store.local_filesystem import LocalFileSystem
from insights_engine.data_store.s3_data_store import S3DataStore


class ScoringEngine:
    """Contains the logic to do the recommendaitons based on the association rules."""

    def __init__(self):
        """Construct a new scoring object."""
        if config.USE_AWS == "True":
            self.s3_bucket = S3DataStore(config.S3_BUCKET_NAME, config.AWS_S3_ACCESS_KEY_ID,
                                         config.AWS_S3_SECRET_ACCESS_KEY)
        else:
            # not really S3
            self.s3_bucket = LocalFileSystem(config.S3_BUCKET_NAME)
        self.ruleset_json = self.s3_bucket.read_json_file(
            os.path.join(config._TRAINED_OBJECT_PREFIX, config.ASSOCIATION_RULE_JSON))
        self.s3_bucket.download_file(
            os.path.join(config._TRAINED_OBJECT_PREFIX, config.ASSOCIATION_RULES_DF),
            config.ASSOCIATION_RULES_DF)
        self.rules_df = pd.read_pickle(config.ASSOCIATION_RULES_DF)
        # Load the package to index and index to package mapping required for scoring.
        package_idx = self.s3_bucket.read_json_file(
            os.path.join(config._TRAINED_OBJECT_PREFIX, config.PACKAGE_IDX_MAPS))
        self.package_to_index_map = package_idx.get("package_to_index_map", {})
        self.index_to_package_map = package_idx.get("index_to_package_map", {})

    def _get_candidate_rules(self, input_stack):
        """Predict the companions for a user's stack."""
        if not isinstance(input_stack, set):
            input_stack = set(input_stack)
        candidate_rules = []
        association_rule_antecedents = self.rules_df['antecedent'].tolist()
        for idx, antecedent in enumerate(association_rule_antecedents):
            if set(antecedent).issubset(input_stack):
                candidate_rules.append(idx)
        candidate_rules = self.rules_df.iloc[candidate_rules]
        candidate_rules = candidate_rules[candidate_rules['lift'] > 0]
        return candidate_rules

    def _create_companion_set(self, candidate_rules, companion_threshold):
        """Select rules based on criteria and recommend companions."""
        # First sort by length of antecedent
        candidate_rules = candidate_rules.sort_values(by='antecedent')
        candidate_rules = candidate_rules[
            candidate_rules['confidence'] > config.MIN_CONFIDENCE_SCORING]
        candidate_rules = candidate_rules[candidate_rules['lift'] >= 0]
        companion = candidate_rules[["consequent", "confidence"]][:companion_threshold]
        recommendations = []
        for index, rule in companion.iterrows():
            for conseq in rule['consequent']:
                recommendations.append({
                    "package_name": self.index_to_package_map[str(conseq)],
                    "cooccurrence_probability": round(rule['confidence'], 4) * 100,
                    "topic_list": []
                })
        return recommendations

    def predict(self, input_stack, companion_threshold):
        """Interfacing method to get companion recommendations."""
        missing, encoded_stack = [], []
        for pkg in input_stack:
            p_id = self.package_to_index_map.get(pkg.lower(), -1)
            if p_id == -1:
                missing.append(pkg)
            else:
                encoded_stack.append(p_id)
        if encoded_stack:
            candidate_rules = self._get_candidate_rules(input_stack=encoded_stack)
            recommendations = self._create_companion_set(candidate_rules, companion_threshold)
        else:
            recommendations = []
        return missing, recommendations
