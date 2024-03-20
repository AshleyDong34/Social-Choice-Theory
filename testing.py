from collections import Counter
import voting_rules as vr
from data_parser import DataParser
import numpy as np


# Define file paths for different ranking data structures
soc_file_path = 'implementation/soc_data/00004-00000001.soc'
soi_file_path = 'implementation/soi_data/00002-00000001.soi'
toc_file_path = 'implementation/toc_data/00002-00000001.toc'
toi_file_path = 'implementation/toi_data/00032-00000007.toi'


# Custom distribution for utility generation
def custom_distribution():
    return np.random.uniform(0,1)

# Test function for a specific voting rule
def test_voting_rule(file_path, voting_rule_function, expected_winner):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, utilities_data = parser.parse()
    num_alternatives = int(metadata['number_alternatives'])
    winner, _ = voting_rule_function(ranking_data, num_alternatives)
    assert winner == expected_winner, f"Test failed: Expected {expected_winner}, got {winner}"


# Define expected winners for each file
expected_soc_winner = 1  
expected_soi_winner = 3 
expected_toc_winner = 3  


# Conduct tests for each file and voting rule
test_voting_rule(soc_file_path, vr.harmonic_scoring_rule, expected_soc_winner)
test_voting_rule(soi_file_path, vr.borda_scoring_rule, expected_soi_winner)
test_voting_rule(toc_file_path, vr.plurality_scoring_rule, expected_toc_winner)


print("basic tests passed successfully!")


def test_probability_vector(file_path, voting_rule_function):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, utilities_data = parser.parse()
    num_alternatives = int(metadata['number_alternatives'])
    probability_vector = voting_rule_function(ranking_data, num_alternatives, randomised=True)

    # Check if the probability vector adds up to one (within a small margin of error)
    assert abs(sum(probability_vector.values()) - 1) < 1e-6, "Test failed: Probability vector does not sum up to 1"

    # Check if all probabilities are non-negative
    assert all(p >= 0 for p in probability_vector.values()), "Test failed: Negative probabilities found"

    print(f"Probability vector test passed for {file_path} using {voting_rule_function.__name__}")

# Testing probability vectors
test_probability_vector(soc_file_path, vr.harmonic_scoring_rule)
test_probability_vector(soi_file_path, vr.borda_scoring_rule)
test_probability_vector(toc_file_path, vr.plurality_scoring_rule)


print("All probability vector tests passed successfully!")

def test_k_approval_multi_winner(file_path, k):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, _ = parser.parse()
    
    winners, scores = vr.k_approval_multi_winner(ranking_data, int(metadata['number_alternatives']), k)
    highest_score = max(scores.values())
    
    assert len(winners) == k, "Incorrect number of winners"

    for winner in winners:
        assert winner in scores, "Winner not in scores dictionary"

    assert all(score <= highest_score for score in scores.values()), "There is a score higher than the highest winner's score"

    print("k-Approval multi-winner test passed")

# Example test call
test_k_approval_multi_winner(toi_file_path, 3)


def test_boutilier_random_harmonic(file_path, iterations=1000):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, _ = parser.parse()
    
    selection_counts = Counter()
    for _ in range(iterations):
        selected_candidate = vr.boutilier_random_harmonic(ranking_data, int(metadata['number_alternatives']))
        selection_counts[selected_candidate] += 1

    assert len(selection_counts) > 0, "No candidate selected"
    assert all(count > 0 for count in selection_counts.values()), "Some candidates never selected"

    print("Boutilier random harmonic test passed")

test_boutilier_random_harmonic(toi_file_path)

def test_irv(file_path):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, _ = parser.parse()
    
    irv_winner = vr.instant_runoff_voting(ranking_data, int(metadata['number_alternatives']))
    assert irv_winner in range(1, int(metadata['number_alternatives']) + 1), "IRV winner is invalid"

    # Further tests can be implemented based on expected outcomes of specific data sets

    print("IRV test passed")

test_irv(toi_file_path)

def test_single_transferable_vote(file_path, num_winners):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, _ = parser.parse()
    
    #print(ranking_data)
    
    winners = vr.single_transferable_vote(ranking_data, int(metadata['number_alternatives']), num_winners)
    print(winners)
    assert len(winners) == num_winners, "Incorrect number of winners in STV"
    assert all(winner in range(1, int(metadata['number_alternatives']) + 1) for winner in winners), "Invalid winner in STV results"

    print("STV test passed")

test_single_transferable_vote(toi_file_path, 3)


def test_utilities(file_path):
    parser = DataParser(file_path, custom_distribution)
    metadata, ranking_data, utilities_data = parser.parse()
    
    print(parser.ties_info)
    
    num_candidates = int(metadata['number_alternatives'])

    for utility_vector in utilities_data:
        # Test 1: Sum of Utilities Equals One
        assert abs(sum(utility_vector) - 1) < 1e-6, "Test failed: Utilities do not sum up to 1"

        # Test 2: Length Equals Number of Candidates
        assert len(utility_vector) == num_candidates, "Test failed: Length of utilities vector does not match number of candidates"

        # Test 3: No Utility Value is Zero
        assert all(utility >= 0 for utility in utility_vector), "Test failed: Utility value is zero"

    print(f"Utilities test passed for {file_path}")

# Testing utilities
test_utilities(soc_file_path)
#test_utilities(soi_file_path)
#test_utilities(toc_file_path)
#test_utilities(toi_file_path)

print("All utility tests passed successfully!")


def test_det_distortion():
    parser = DataParser(soi_file_path, custom_distribution)
    _,_,_ = parser.parse()
    winner = 2  # Example winner candidate id
    distortion = vr.det_distortion(winner, parser, num_iteres=10)
    assert distortion >= 0, "Distortion should be non-negative"

test_det_distortion()

def test_multi_winner_distortion():
    parser = DataParser(toc_file_path, custom_distribution)
    _,_,_ = parser.parse()
    winners = [1, 2, 3]  # Example list of winners
    _, worst_distortion = vr.multi_winner_distortion(winners, parser, num_iteres=10)
    assert worst_distortion >= 0, "Distortion should be non-negative"

test_multi_winner_distortion()


def test_rand_distortion():
    parser = DataParser(toi_file_path, custom_distribution)
    _,_,_ = parser.parse()
    probability_vector = [0.25, 0.25, 0.25, 0.25]  # Example probabilities
    distortion = vr.rand_distortion(parser, probability_vector)
    assert distortion >= 0, "Distortion should be non-negative"

test_rand_distortion()

def test_social_welfare():
    parser = DataParser(soc_file_path, custom_distribution)
    _,_,_ = parser.parse()
    utility_dic = vr.social_welfare(parser)
    assert all(value >= 0 for value in utility_dic.values()), "Social welfare values should be non-negative"

test_social_welfare()

print("All distortion and social welfare tests passed successfully!")



