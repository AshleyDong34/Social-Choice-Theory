import random

####################################### The helper scoring functions ###############################################

def scoring_rule(ranking_data, scoring_vector, num_alternatives):
    """
    Calculates the scores of candidates based on the provided scoring rule.

    Args:
        ranking_data (list): A list of tuples, each containing the number of voters for a specific ranking and the ranking itself.
        scoring_vector (list): A list of scores corresponding to each rank in the ranking.
        num_alternatives: number of alternatives

    Returns:
        dict: A dictionary with candidate identifiers as keys and their calculated scores as values.
    """
    # Initialize candidate scores for alternatives, starting from 0
    candidate_scores = {i: 0 for i in range(1, num_alternatives + 1)}
 
    # Process each voter's ranking
    for num_voters, ranks in ranking_data:
        # Iterate over each candidate's rank in the sequence
        for rank_index, candidate in enumerate(ranks):
            # Ensure the rank index is within the length of the scoring vector
            if rank_index < len(scoring_vector):
                # Add the score to the candidate times the number of voters with this ranking
                candidate_scores[candidate] += scoring_vector[rank_index] * num_voters
    
    

    return candidate_scores

# returns a probability distribution over the candidates based on the scoring rule and total score
def normalized_scoring_vector(candidate_scores):
    """
    Normalizes the scores of candidates to form a probability distribution.

    Args:
        candidate_scores (dict): A dictionary with candidate identifiers as keys and their raw scores as values.

    Returns:
        dict: A dictionary with candidate identifiers as keys and their normalized scores as values.

    Raises:
        ValueError: If the total score is zero, making normalization impossible.
    """
    total_score = sum(candidate_scores.values())
    if total_score == 0:
        raise ValueError("Total score is zero, normalization not possible.")
    
    normalized_scores = {candidate: score / total_score for candidate, score in candidate_scores.items()}
    return normalized_scores

# checks the flag for randomised scoring and applies the scoring rule
def apply_scoring_rule(ranking_data, num_alternatives, scoring_vector, randomised):
    
    """
    Applies a scoring rule to ranking data and returns the results, either as normalized scores or as the highest-scoring candidate.

    Args:
        ranking_data (list): A list of tuples containing ranking information.
        num_alternatives: number of alternatives
        scoring_vector (list): A list of scores for ranking positions.
        randomised (bool): A flag indicating whether to use normalized scoring.

    Returns:
        Depending on the value of 'randomised':
        - If True: Returns a dictionary of normalized scores.
        - If False: Returns a tuple containing the highest-scoring candidate and their score.
    """
    
    candidate_scores = scoring_rule(ranking_data, scoring_vector, num_alternatives)
    if randomised:
        return normalized_scoring_vector(candidate_scores)
    else:
        max_score_candidate = max(candidate_scores, key=candidate_scores.get)
        return max_score_candidate, candidate_scores[max_score_candidate]

################################# The scoring rules ##########################################
                    
### Basic scoring rules with randomisation option ###

# plurality scoring rule - 1 point for first place, 0 points for all other places
def plurality_scoring_rule(ranking_data, num_alternatives, randomised=False):
    """
    Calculates the scores of candidates using the plurality scoring rule.

    Args:
        ranking_data (list): A list of tuples, each containing the number of voters for a specific ranking and the ranking itself.
        num_alternatives: number of alternatives
        randomised (bool): A flag indicating whether to return normalized scores or the highest-scoring candidate.

    Returns:
        Depending on the value of 'randomised':
        - If True: Returns a dictionary of normalized scores.
        - If False: Returns a tuple containing the highest-scoring candidate and their score.
    """
    scoring_vector = [1] + [0] * (num_alternatives - 1)
    return apply_scoring_rule(ranking_data, num_alternatives, scoring_vector, randomised)

# borda scoring rule - n-1 points for first place, n-2 points for second place, ..., 0 points for last place
def borda_scoring_rule(ranking_data, num_alternatives, randomised=False):
    """
    Calculates the scores of candidates using the Borda count scoring rule.

    In Borda count, each position on a ballot is assigned a point value, with higher positions 
    receiving more points. The scores for each candidate are summed across all ballots.

    Args:
        ranking_data (list): A list of tuples, each containing the number of voters for a specific ranking and the ranking itself.
        num_alternatives: number of alternatives
        randomised (bool): A flag indicating whether to return normalized scores or the highest-scoring candidate.

    Returns:
        Depending on the value of 'randomised':
        - If True: Returns a dictionary of normalized scores.
        - If False: Returns a tuple containing the highest-scoring candidate and their score.
    """
    scoring_vector = list(range(num_alternatives - 1, -1, -1))
    return apply_scoring_rule(ranking_data, num_alternatives, scoring_vector, randomised)

# harmonic scoring rule - 1 point for first place, 1/2 points for second place, 1/3 points for third place, ...
def harmonic_scoring_rule(ranking_data, num_alternatives, randomised=False):
    """
    Calculates the scores of candidates using the harmonic scoring rule.

    In the harmonic scoring rule, each position on a ballot is assigned a point value inversely 
    proportional to its rank (1 for 1st place, 1/2 for 2nd place, etc.). The scores for each 
    candidate are summed across all ballots.

    Args:
        ranking_data (list): A list of tuples, each containing the number of voters for a specific ranking and the ranking itself.
        num_alternatives: number of alternatives
        randomised (bool): A flag indicating whether to return normalized scores or the highest-scoring candidate.

    Returns:
        Depending on the value of 'randomised':
        - If True: Returns a dictionary of normalized scores.
        - If False: Returns a tuple containing the highest-scoring candidate and their score.
    """

    scoring_vector = [1 / (i + 1) for i in range(num_alternatives)]
    return apply_scoring_rule(ranking_data, num_alternatives, scoring_vector, randomised)

### multi winner scoring rules ###

def k_approval_multi_winner(ranking_data, num_alternatives, k):
    """
    Implements the k-approval multi-winner scoring rule.

    Args:
        ranking_data (list): A list of tuples containing ranking information.
        num_alternatives: number of alternatives
        k (int): The number of top-ranked candidates to approve.

    Returns:
        tuple: A tuple containing the list of top 'k' candidates and their corresponding scores.
    """

    # Create a scoring vector for k-approval
    scoring_vector = [1 if i < k else 0 for i in range(num_alternatives)]

    # Calculate candidate scores
    candidate_scores = scoring_rule(ranking_data, scoring_vector, num_alternatives)

    # Sort candidates by score and select the top k
    top_candidates = sorted(candidate_scores, key=candidate_scores.get, reverse=True)[:k]
    top_scores = {candidate: candidate_scores[candidate] for candidate in top_candidates}

    return top_candidates, top_scores

def boutilier_random_harmonic(ranking_data, num_alternatives):
    """
    Chooses an alternative based on a combination of random selection and harmonic scoring.

    Args:
        ranking_data (list): A list of tuples containing ranking information.
        num_alternatives: number of alternatives

    Returns:
        int: The identifier of the selected alternative.
    """
    # Choose an alternative
    if random.random() < 0.5:
        # Select uniformly at random
        selected_alternative = random.randint(1, num_alternatives)
    else:
        # Select based on harmonic scores
        normalized_scores = harmonic_scoring_rule(ranking_data, num_alternatives, randomised=True)
        # make two lists from the dictionary normalized_scores
        candidates, probabilities = zip(*normalized_scores.items())
        # select one candidate from the list candidates, with the probabilities from the list probabilities
        selected_alternative = random.choices(candidates, weights=probabilities, k=1)[0]

    return selected_alternative

# here is how fractional redistribution of votes works in stv:


# For each ranking, eg 1 < 2 < 3 < 4, only  candidate 1 gets a full vote, a vote score of 1
# If quota is reached with candidate 1, the surplus is used to calculate the new vote score for candidate 2, which is usually lower now.
# This means that this ranking is now 2 < 3 < 4, and the vote score for candidate 2 is now the ratio of surplus/canidate 1's total votes multiplied by PREVIOUS value
# If there are no candidates that reach the quota. then the lowest votes candidate is eliminated and their votes 'given' to the next preference in each voter's ranking
# repeat until the number of winners is reached

def single_transferable_vote(ranking_data, num_alternatives, num_winners):
    
    """
    Executes the Single Transferable Vote (STV) method for committee elections with fractional surplus redistribution.

    This method processes the voting data to elect a specified number of candidates. It uses an STV mechanism where each voter's ballot has a fractional value, initially set to 1. The method involves electing candidates who reach a vote quota and redistributing the surplus votes of elected candidates to the next preferences on the ballots. If no candidate reaches the quota, the candidate with the fewest votes is eliminated, and their votes are redistributed. This process continues until the required number of winners is elected.

    Args:
        ranking_data (list): A list of tuples, each containing the number of voters and their respective ranking of candidates.
        num_alternatives: number of alternatives
        num_winners (int): The number of candidates to be elected.

    Returns:
        list: A list of identifiers of the elected candidates.
    """
    
    total_votes = sum(num_voters for num_voters, _ in ranking_data)
    quota = total_votes // (num_winners + 1) + 1

    ballots = [{'ranking': ranks, 'value': 1.0} for _, ranks in ranking_data for _ in range(_)]
    elected_candidates = set()
    candidate_votes = {i: 0 for i in range(1, num_alternatives + 1)}

    while len(elected_candidates) < num_winners:
        for ballot in ballots:
            for candidate in ballot['ranking']:
                if candidate not in elected_candidates:
                    candidate_votes[candidate] += ballot['value']
                    break
        
        for candidate, votes in candidate_votes.items():
            if votes >= quota and candidate not in elected_candidates:
                elected_candidates.add(candidate)
                surplus = votes - quota
                surplus_ratio = surplus / votes
                for ballot in ballots:
                    if ballot['ranking'][0] == candidate:
                        ballot['value'] *= surplus_ratio
                        ballot['ranking'].pop(0)
                break
        else:
            min_votes = min(candidate_votes.values())
            for candidate, votes in candidate_votes.items():
                if votes == min_votes:
                    for ballot in ballots:
                        if candidate in ballot['ranking']:
                            ballot['ranking'].remove(candidate)
                    candidate_votes.pop(candidate)
                    break

    return list(elected_candidates)



# Other Scoring Rules

# irv scoring rule - each round, check if a candidate has more than half of the first place votes, if not, eliminate the candidate with the fewest votes
def instant_runoff_voting(ranking_data, num_alternatives):
    """
    Implements the Instant Runoff Voting (IRV) electoral system.

    Args:
        ranking_data (list): A list of tuples containing ranking information.
        num_alternatives: number of alternatives

    Returns:
        The winning candidate identifier, or a list of candidates in the event of a tie.
    """
    # Determine the number of alternatives and init the candidate scores
    candidate_scores = {i: 0 for i in range(1, num_alternatives + 1)}

    # Convert ranking data into a list of ballots
    ballots = []
    for num_voters, ranks in ranking_data:
        ballots.extend([ranks] * num_voters)

    # Conduct the IRV process
    while True:
        # Count the first-choice votes for each candidate
        for ballot in ballots:
            # check if ballot is empty
            if ballot:
                candidate_scores[ballot[0]] += 1

        # Check if any candidate has more than half of the votes
        total_votes = sum(candidate_scores.values())
        for candidate, votes in candidate_scores.items():
            if votes > total_votes / 2:
                return candidate  # Candidate wins

        # Find the candidate(s) with the fewest votes
        fewest_votes = min(candidate_scores.values())
        
        # list comprehension, returns a list of candidates, where the candidate has the fewest votes
        candidates_to_eliminate = [candidate for candidate, votes in candidate_scores.items() if votes == fewest_votes]

        # If all remaining candidates have the fewest votes, tiebreaker
        if len(candidates_to_eliminate) == len(candidate_scores):
            return candidates_to_eliminate  # Tiebreaker, return all, could be randomised for a candidate to win.

        # Eliminate the candidate(s) with the fewest votes
        for candidate in candidates_to_eliminate:
            del candidate_scores[candidate]

        # Remove the eliminated candidate(s) from each ballot
        for ballot in ballots:
            ballot[:] = [candidate for candidate in ballot if candidate not in candidates_to_eliminate]

def det_distortion(winner, parser, num_iteres=1, average=True):
    
    """
    Calculates the distortion of a given winner in a deterministic voting rule for that setting. Could be average or worst case.
    Args:
        winner (int): The identifier of the winning candidate.
        parser (DataParser): An instance of the DataParser class, used to parse and handle the data.
        num_iteres (int, optional): The number of iterations to average over for distortion calculation. Defaults to 1.
        average (bool, optional): Flag to determine if the average distortion over iterations is returned or the worst case. Defaults to True.

    Returns:
        float: The calculated distortion value.
    """
    
    worst_distortion, total_distortion = 0, 0
    
    for iter in range(num_iteres):
        utility_dic = social_welfare(parser)
                
        # Finding the candidate with optimal social welfare
        optimal_sw = max(utility_dic.values())
        winner_sw = utility_dic[winner]

        # Calculating distortion
        if winner_sw > 0:
            distortion = optimal_sw / winner_sw
            total_distortion += distortion
            
            if distortion > worst_distortion:
                worst_distortion = distortion
        else:
            # Raise an error if winner's social welfare is zero
            raise ValueError(f"Winner's social welfare is zero in iteration {iter}. Please check the utility distribution or input data.")

    return total_distortion/num_iteres if average else worst_distortion

# find the max distortion of the winners
def multi_winner_distortion(winners, parser, num_iteres=1, average=True):
    """
    Calculates the distortion for a list of winners in a multi-winner decision-making process.

    Args:
        winners (list): A list of winning candidate identifiers.
        parser (DataParser): An instance of the DataParser class.
        num_iteres (int, optional): Number of iterations for averaging. Defaults to 1.
        average (bool, optional): Flag to return average distortion over iterations. Defaults to True.

    Returns:
        tuple: A tuple containing the candidate with the worst distortion and the corresponding distortion value.
    """
    (worst_cand,worst_distortion) = (None,0)
    for winner in winners:
        distortion = det_distortion(winner, parser, num_iteres, average)
        if distortion > worst_distortion:
            (worst_cand,worst_distortion) = (winner, distortion)
    return worst_cand, worst_distortion

def rand_distortion(parser, probability_vector, method = "expected", num_iters = 100):
    """
    Calculates the distortion based on a random selection method.

    Args:
        parser (DataParser): An instance of the DataParser class.
        probability_vector (list): A list of probabilities for each candidate.
        method (str, optional): The method to calculate distortion ('expected' or 'average'). Defaults to "expected".
        num_iters (int, optional): Number of iterations for averaging in 'average' method. Defaults to 100.

    Returns:
        float: The calculated distortion value.
    """
    utility_dic = social_welfare(parser)
    
    if method == "expected":
        distortion_vector = [0 for _ in range(len(probability_vector))]
        for i, prob in enumerate(probability_vector):
            distortion_vector[i] = prob*utility_dic[i+1]
        return max(utility_dic.values())/sum(distortion_vector)
    
    elif method == "average":
        total_social_welfare = 0
        for _ in range(num_iters):
            winner = random.choices(range(1,len(probability_vector)+1), weights=probability_vector, k=1)[0]
            total_social_welfare += utility_dic[winner]
        return max(utility_dic.values())/(total_social_welfare/num_iters)

# helper social welfare finder for candidates

def social_welfare(parser):
    """
    Calculates the social welfare for each candidate.

    Args:
        parser (DataParser): An instance of the DataParser class, used to parse and handle the data.

    Returns:
        dict: A dictionary with candidate identifiers as keys and their corresponding social welfare as values.
    """
    num_alternatives = int(parser.metadata['number_alternatives'])

    # this is wrong, becasue ties info is for only one voters rankings at a time, not all voters.
    utilities_data = parser.generate_utilities()
    utility_dic = {i: 0 for i in range(1, num_alternatives + 1)}

    # Summing utilities for each candidate
    for voter_utility in utilities_data:
        for i, utility in enumerate(voter_utility):
            utility_dic[i+1] += utility

    return utility_dic


