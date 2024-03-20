import random
import re
import numpy as np
from preflibtools.instances import OrdinalInstance

class DataParser:
    
    """
    A parser for handling social ranking data files. 

    This class is responsible for parsing data files that contain social ranking information, organizing 
    this data into a structured format, and generating utilities based on a provided distribution function.
    It fills in incomplete rankings and also breaks ranking data with ties

    Attributes:
        file_path (str): Path to the data file.
        metadata (dict): Dictionary to store metadata extracted from the file.
        ranking_data (list(int, list)): lists and their pairs to store organized ranking data.
        utilities_data (list): List to store generated utilities data.
        utility_distribution (function): Distribution function to generate utility values.

    Methods:
        parse(): Parses the data file and organizes the data.
        parse_ranks(str): Parses rank strings from the data file - breaks ranking data with ties.
        complete_rankings(list, list): Completes rankings for all candidates - fills in missing candidates.
        generate_utilities(list, int): Generates utility values based on the parsed data.
    """
    
    def __init__(self, file_path = '', utility_distribution = None):
        """
        Initializes the DataParser with a file path and a utility distribution function.

        Args:
            file_path (str): The path to the file containing the ranking data.
            utility_distribution (function): A function that generates utility values.
        """
        # if we are using preflibtools, then we can just pass a empty string for the file path, if they are using a url instead of a file path
        self.file_path = file_path
        self.metadata = {}
        self.ranking_data = []
        self.utilities_data = []
        self.utility_distribution = utility_distribution if utility_distribution is not None else lambda: np.random.uniform(0, 1)
        self.ties_info = []

    def parse(self):
        
        """
        Parses the data file, extracting metadata, rankings, and generating utilities.

        Reads the data file, line by line, extracting metadata, organizing the ranking data, and 
        generating utilities for each set of rankings.

        Returns:
            tuple: A tuple containing three elements: 
                   - metadata (dict): Extracted metadata.
                   - ranking_data (list( int, list)): Organized ranking data, paired with the number of voters for that ranking
                   - utilities_data (list): Generated utilities for each ranking.
        """
        
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    if ': ' in line:
                        key, value = line[2:].split(': ', 1)
                        self.metadata[key.lower().replace(' ', '_')] = value
                else:
                    if line:
                        voter, ranks_str = line.split(': ')
                        num_voters = int(voter)
                        ranks, ties_info = self.parse_ranks(ranks_str)
                        ranks, ties_info = self.complete_rankings(ranks, ties_info)
                        self.ties_info.append(ties_info)
                        self.ranking_data.append((num_voters, ranks))

        self.utilities_data = self.generate_utilities()
        return self.metadata, self.ranking_data, self.utilities_data

    def parse_ranks(self, ranks_str):
        """
        Parses a string of ranks into structured rank and ties information.

        Args:
            ranks_str (str): A string representing the ranks and ties in the ranking data.

        Returns:
            tuple: A tuple containing two elements:
                   - ranks (list): A list of ranks.
                   - ties_info (list): A list of tuples with information about ties.
        """
        # only split on commas that are not inside curly braces
        ranks_parts = re.split(r',(?![^{]*\})', ranks_str)
        ranks = []
        ties_info = []

        for part in ranks_parts:
            if '{' in part and '}' in part:
                tied_candidates = [int(num) for num in part.strip('{}').split(',')]
                ranks.extend(tied_candidates)
                ties_info.append((tied_candidates, 'tie'))  # Mark as tie
            else:
                candidate = int(part)
                ranks.append(candidate)
                ties_info.append(([candidate], 'single'))  # Mark as single

        return ranks, ties_info


    def complete_rankings(self, ranks, ties_info):
        
        """
        Completes the rankings for all alternatives, marking unranked alternatives.

        Args:
            ranks (list): The list of currently ranked alternatives.
            ties_info (list): The list containing information about ties and their types.

        Returns:
            tuple: A tuple containing the updated ranks and ties_info lists.
        """
        
        num_alternatives = int(self.metadata['number_alternatives'])
        ranked = set(r for tie_group, _ in ties_info for r in tie_group)
        unranked = set(range(1, num_alternatives + 1)) - ranked
        
        random.shuffle(list(unranked))  # Shuffle the unranked alternatives

        for u in unranked: # should be random order
            
            ranks.append(u)
            ties_info.append(([u], 'unranked'))  # Mark as unranked

        return ranks, ties_info



    def generate_utilities(self):
        """
        Generates utility values for the voters that voted for the same ranking based on the parsed ranking data.

        Args:
            ties_info (list): List containing information about ties in the rankings.
            num_voters (int): Number of voters involved in the ranking.

        Returns:
            list: A list of random utility values for each voter for their rankings.
        """
        num_candidates = int(self.metadata['number_alternatives'])
        voter_utilities = []
        
        # ties info is like this: [ [([4], 'single'), ([1, 2, 3], 'tie')],   [...],  ... ] each list represents the rankings 
        # for a set of voters who voted the same ranking

        for i, (num_voters, _) in enumerate(self.ranking_data):
            
            for _ in range(num_voters):
                
                utilities = np.zeros(num_candidates)
                # Generate a utility value for each ranked position (not each candidate)
                num_ranked_positions = sum([len(g) for g, t in self.ties_info[i] if t != 'unranked'])
                random_utilities = np.array([self.utility_distribution() for _ in range(num_ranked_positions)])
                random_utilities /= random_utilities.sum()  # Normalize
                random_utilities = np.sort(random_utilities)[::-1]  # Sort in descending order (highest utility first
                #print(random_utilities)

                util_index = 0  # Index for the generated utilities

                for group, group_type in self.ties_info[i]:
                    if group_type == 'unranked':
                        for c in group:
                            utilities[c - 1] = 0
                    elif group_type == 'single':
                        utilities[group[0] - 1] = random_utilities[util_index]
                        util_index += 1
                    else:
                        avg_utility = np.mean(random_utilities[util_index:util_index + len(group)])
                        util_index += len(group)
                        for c in group:
                            utilities[c - 1] = avg_utility

                voter_utilities.append(utilities.tolist())
        self.utilities_data = voter_utilities
        return voter_utilities
    

    def parse_data(self, instance, utility_distribution):
        
        self.file_path = ''
        self.metadata = {}
        self.ranking_data = []
        self.utilities_data = []
        self.utility_distribution = utility_distribution
        self.ties_info = []
        self.metadata = {
            "file_path": instance.file_path,
            "file_name": instance.file_name,
            "data_type": instance.data_type,
            "modification_type": instance.modification_type,
            "relates_to": instance.relates_to,
            "related_files": instance.related_files,
            "title": instance.title,
            "description": instance.description,
            "publication_date": instance.publication_date,
            "modification_date": instance.modification_date,
            "number_alternatives": instance.num_alternatives,
            "alternatives_name": instance.alternatives_name,
            "number_voters": instance.num_voters
        }
        
        self.ranking_data = []
        self.ties_info = []
        
        # the order should be, check for ties, deal with ties, add to ties info then, check for incomplete, 
        # deal with incomplete, add to ties info. We also need to build ranking data alongside ties info.
        for order in instance.orders:
            num_voters = instance.multiplicity[order]
            ranks, ties = self.parse_order_to_ranks(order)

            ranks, ties = self.complete_rankings_data(ranks, ties)
            self.ties_info.append(ties)
            self.ranking_data.append((num_voters, ranks))

            
        self.utilities_data = self.generate_utilities()
        return self.metadata, self.ranking_data, self.utilities_data


    def parse_order_to_ranks(self, order):
        """
        Converts a PrefLib order into a list of ranks and tie information.

        Args:
            order (tuple): A tuple representing the order in PrefLib data format.

        Returns:
            tuple: A tuple containing two elements:
                - ranks (list): A list of ranks.
                - ties_info (list): A list of tuples with information about ties.
        """
        ranks = []
        ties_info = []

        for group in order:
            if len(group) > 1:
                # Handle ties
                ranks.extend(list(group))
                ties_info.append((list(group), 'tie'))
            else:
                # Handle single ranked candidates
                ranks.extend(list(group))
                ties_info.append((list(group), 'single'))

        return ranks, ties_info
        
    def complete_rankings_data(self, ranks, ties_info):
        """
        Completes the rankings for all alternatives, marking unranked alternatives.

        Args:
            ranks (list): The list of currently ranked alternatives.
            ties_info (list): The list containing information about ties and their types.

        Returns:
            tuple: A tuple containing the updated ranks and ties_info lists.
        """
        num_alternatives = int(self.metadata['number_alternatives'])
        ranked = set(r for tie_group, _ in ties_info for r in tie_group)
        unranked = set(range(1, num_alternatives + 1)) - ranked

        unranked_list = list(unranked)
        random.shuffle(unranked_list)

        for u in unranked_list:
            ranks.append(u)
            ties_info.append(([u], 'unranked'))

        return ranks, ties_info
                