import sys
import itertools


class Apriori():
    def __init__(self, input_file, output_file, min_s_count, confidence, include_support):
        self.min_s_count = min_s_count
        self.input_file = input_file
        self.output_file = output_file
        self.confidence = confidence
        self.items_count = self.get_all_items()
        self.frequent_patterns = self.get_frequent_patterns(include_support)

    def get_frequent_patterns(self, include_support):
        frequent_patterns = []
        frequent_patterns_supp = []
        min_support_count = self.min_s_count
        candidate_patterns_1_count = self.items_count
        candidate_patterns_1 = list(candidate_patterns_1_count.keys())
        frequent_pattern = [itemset for itemset in candidate_patterns_1 if
                            candidate_patterns_1_count[itemset] >= min_support_count]
        frequent_pattern_supp = [([itemset], candidate_patterns_1_count[itemset]) for itemset in candidate_patterns_1 if
                                 candidate_patterns_1_count[itemset] >= min_support_count]
        frequent_patterns.extend(frequent_pattern)
        frequent_patterns_supp.extend(frequent_pattern_supp)
        flag = 0
        while len(frequent_pattern) != 0:
            if flag == 0:
                candidate_pattern = self.candidate_generation_1(frequent_pattern, len(frequent_pattern))
                flag = 1
            else:
                candidate_pattern = self.candidate_generation(frequent_pattern, len(frequent_pattern))
            candidate_pattern = self.prune(candidate_pattern, frequent_pattern)
            candidate_pattern_count = self.get_support_count(candidate_pattern)
            frequent_pattern = [itemset for itemset in candidate_pattern if
                                candidate_pattern_count[tuple(itemset)] >= min_support_count]
            frequent_pattern_supp = [(itemset, candidate_pattern_count[tuple(itemset)]) for itemset in candidate_pattern if
                                     candidate_pattern_count[tuple(itemset)] >= min_support_count]
            frequent_patterns.extend(frequent_pattern)
            frequent_patterns_supp.extend(frequent_pattern_supp)
        return frequent_patterns_supp if include_support else frequent_patterns

    def prune(self, candidate_pattern, frequent_pattern):
        # this method prunes the candidate patterns generated
        # any k -1 subset of k-set pattern is not in k-1 non overlap patterns then
        # it is also not present k-set non overlap pattern so can be removed
        for pattern in candidate_pattern:
            k_subset_list = list(itertools.combinations(pattern, len(pattern)-1))
            k_subset_list = [list(k) for k in k_subset_list]
            for kitem in k_subset_list:
                if len(kitem) == 1:
                    kitem = kitem[0]
                if kitem in frequent_pattern:
                    continue
                else:
                    candidate_pattern.remove(pattern)
                    break
        return candidate_pattern

    def candidate_generation_1(self, pattern, length):
        candidate = []
        for i in range(0, length):
            element1 = pattern[i]
            for j in range(i+1, length):
                element2 = pattern[j]
                new_list = list()
                new_list.append(element1)
                new_list.append(element2)
                candidate.append(self.sort_pattern(new_list))
        return candidate

    def candidate_generation(self, pattern, length):
        # this function takes a k-pattern and joins with itself to give k+1 pattern
        candidate = []
        for i in range(0, length):
            element1 = pattern[i]
            for j in range(i+1, length):
                element2 = pattern[j]
                len_each_pattern = len(element1)
                if element1[0:len_each_pattern-1] == element2[0:len_each_pattern-1]:
                        next_list = list(element1[0:len_each_pattern-1])
                        next_list.append(element1[len_each_pattern-1])
                        next_list.append(element2[len_each_pattern-1])
                        candidate.append(self.sort_pattern(next_list))
        return candidate

    def sort_pattern(self, itemset):
        sorted_pattern = sorted(itemset, key=lambda x: self.items_count[x] if x in self.items_count else 0, reverse=True)
        return sorted_pattern

    def get_all_items(self):
        count_dict = {}
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
            self.min_s_count = (self.min_s_count * len(lines))/100
            for line in lines:
                trans_list = line.strip().split(',')
                for item in trans_list:
                    if item in count_dict:
                        count_dict[str(item)] += 1
                    else:
                        count_dict[str(item)] = 1
        f.close()
        return count_dict

    def get_support_count(self, pattern):
        count_dict = {}
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                trans_list = line.strip().split(',')
                for itemset in pattern:
                    if tuple(itemset) in count_dict:
                        if self.check_pattern_exist(trans_list, itemset):
                            count_dict[tuple(itemset)] += 1
                    else:
                        if self.check_pattern_exist(trans_list, itemset):
                            count_dict[tuple(itemset)] = 1
                        else:
                            count_dict[tuple(itemset)] = 0
        f.close()
        return count_dict

    def check_pattern_exist(self, transaction, itemset):
        # takes two lists containing items and checks if itemset list
        # is present in the transaction
        check = True
        for item in itemset:
            if item not in transaction:
                check = False
                break
        if check:
            return True
        else:
            return False


def create_dictionary(frequent_patterns):
    """ This takes frequent patterns and creates a dictionary out of it ."""
    count = {}
    for pattern in frequent_patterns:
        pattern[0].sort()
        count[tuple(pattern[0])] = pattern[1]
    return count


def generate_association_rules(frequent_patterns, min_confidance):
    """ This function generates association rules from the frequent patterns """
    frequent_patterns_dict = create_dictionary(frequent_patterns)
    association_rules_list = []
    for pattern in frequent_patterns:
        if len(pattern[0]) == 1:
            pass
        else:
            for i in range(1, len(pattern[0])):
                pattern[0].sort()
                sub_patterns = itertools.combinations(pattern[0], i)
                for each_sub_pattern in sub_patterns:
                    a = list(each_sub_pattern)
                    a.sort()
                    b = set(pattern[0]) - set(each_sub_pattern)
                    b = list(b)
                    b.sort()
                    confidance = (frequent_patterns_dict[tuple(pattern[0])]/frequent_patterns_dict[tuple(a)])*100
                    if confidance >= min_confidance:
                        if (a, b) not in association_rules_list:
                            association_rules_list.append((a, b))
    return association_rules_list


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    min_s_count = float(sys.argv[3])
    confidence = float(sys.argv[4])
    apriori = Apriori(input_file, output_file, min_s_count, confidence, True)
    rules = generate_association_rules(apriori.frequent_patterns, confidence)
    print(len(rules))
