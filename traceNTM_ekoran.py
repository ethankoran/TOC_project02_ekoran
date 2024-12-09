import sys
import os

# TURING class definition -> stores data from the input file into one data structure for easy access
# throughout the program
class TURING:
    def __init__(self, name, deterministic, states, sigma, gamma, start, accept, reject, transitions):
        self.name = name
        self.deterministic = deterministic
        self.states = states
        self.sigma = sigma
        self.gamma = gamma
        self.start = start
        self.accept = accept
        self.reject = reject
        self.transitions = transitions

    # dump function prints out a formatted output of the turing machine's info
    def dump(self):
        print(f"{'Deterministic' if self.deterministic else 'Nondeterministic'} Turing Machine Info:")
        print(f"{'Machine Name:':>17} {self.name}")
        print(f"{'States:':>17} {', '.join(self.states)}")
        print(f"{'Sigma:':>17} {', '.join(self.sigma)}")
        print(f"{'Gamma:':>17} {', '.join(self.gamma)}")
        print(f"{'Start State:':>17} {self.start}")
        print(f"{'Accept State:':>17} {self.accept}")
        print(f"{'Reject State:':>17} {self.reject}")
        
# Basic usage function to catch any errors when running the program
def usage(status):
    print('Usage Error:')
    print('\tpython3 traceNTM_ekoran.py $FILE $INPUT_STRING $STEP_LIMIT')
    sys.exit(status)

# Function to read in the turing machine from the input file and return an instance of the TURING
# class containing all the info
def build_TM(file):
    with open(file, mode='r', newline='') as TM:
        machine_name = TM.readline().strip()
        deterministic = True if 'Deterministic' in machine_name else False
        states = TM.readline().strip().split(',')
        sigma = TM.readline().strip().split(',')
        gamma = TM.readline().strip().split(',')
        start = TM.readline().strip()
        accept = TM.readline().strip()
        reject = TM.readline().strip()
        transitions = [line.strip().split(',') for line in TM]

    return TURING(machine_name, deterministic, states, sigma, gamma, start, accept, reject, transitions)

# Function that recreates and prints the order of configurations that the turing machine went through in  
# order to reach the accept state
def backtrack_path(TM, tree):
    # If the TM is deterministic, the tree will already containt the correct path, as there is only one
    # configuration per level
    if TM.deterministic:
        for config in tree:
            left, head, right, _ = config[0]
            print(f'    {left} {head} {right}')
        branches = sum([len(level) for level in tree])
        print(f'Degree of Nondeterminism: {branches / len(tree)}')

    # If TM is non deterministic, we need to back track from the accept state configuration to find the  
    # path it took from the beginning configuration using the following method
    #   *  Start at the last level of the tree with the accept state configuration
    #   *  Use the previous state of that configuration to identify the previous configuration in the 
    #      level above
    #   *  Repeat until you get back to the first level of the tree
    else:
        curr = [config for config in tree[-1] if TM.accept in config][0]
        path = [curr]
        for i in range(len(tree) - 2, -1, -1):
            prev_state = curr[3]
            for config in tree[i]:
                if config[1] == prev_state:
                    path.append(config)
                    curr = config
                    break
        path.reverse()
        for config in path:
            left, head, right, _ = config
            print(f'    {left} {head} {right}')

        # Degree of nondeterminism = number of branches in tree / max depth of tree
        branches = sum([len(level) for level in tree])
        print(f'Degree of Nondeterminism: {branches / len(tree)}')

        # Print out a table similar to that in example 4.2 containing the following information of each level of the tree
        #   *  Number of configurations
        #   *  Number of outgoing transitions
        #   *  Number of nonleaf branches
        #   *  Ratio of outgoing transitions to nonleaves
        print(f'Nondeterminism Summary:')
        print(f"{'Level':>9}{'# Configs':>14}{'# Outgoing Transitions':>27}{'# NonLeaves':>16}{'Transitions/NonLeaves':>26}")
        for level, branch in enumerate(tree):
            configs = len(branch)
            try:
                outgoing = len(tree[level+1])
            except IndexError:
                outgoing = 0
            nonleaves = 0
            for config in branch:
                if config[1] == TM.reject or config[1] == TM.accept:
                    continue
                try:
                    head_char = config[2][0]
                except IndexError:
                    continue
                if (len([transition for transition in TM.transitions if transition[0] == config[1] and head_char == transition[1]])):
                    nonleaves += 1
            try:
                ratio = outgoing/nonleaves
            except ZeroDivisionError:
                ratio = 0
            print(f"{level:>8}{configs:>14}{outgoing:>27}{nonleaves:>16}{ratio:>26}")         

# Function that uses BFS to trace the turing machine on a given input string, stopping after the string is accepted,
# the string is rejected, or the tree reaches the maximum step limit defined by the user
def turing_machine_BFS(TM, input, limit):
    curr = TM.start
    # Configuration = (string left of head, current state, string right of head, previous state)
    frontier = [[('', curr, input, None)]]
    tree = []

    while frontier:
        level = frontier.pop(0)
        tree.append(level)

        if len(tree) > limit:
            print(f"Execution stopped after the max step limit: {limit}")
            return tree

        next_level = []
        # Take each configuration in the level and find the possible valid transitions out of that configuration
        for config in level:
            input_seen, curr_state, input_next, _ = config
            head_char = input_next[0]
            # find all transitions branching off of current state
            for transition in [transition for transition in TM.transitions if transition[0] == curr_state]:
                _, next_char, next_state, write_char, direction = transition
                if next_char == head_char: # check if transition is valid based on what char the head is pointing to
                    # add next configuration based on the direction the transition moves the head
                    if direction == 'R':
                        next_level.append((input_seen + write_char, next_state, input_next[1:], curr_state))
                    elif direction == 'L':
                        next_level.append((input_seen[:-1], next_state, input_seen[-1] + write_char + input_next[1:], curr_state))
                    elif direction == 'S':
                        next_level.append((input_seen, next_state, write_char + input_next[1:], curr_state))
                    if next_state == TM.accept: # if you transition to the accept state, stop computing and output results
                        tree.append(next_level)
                        print(f"Transitions Simulated: {sum([len(level) for level in tree]) - 1}")
                        if len(tree) - 1 == 1:
                            print('String accepted in 1 step')
                        else:
                            print(f"String accepted in {len(tree) - 1} steps:")
                        backtrack_path(TM, tree)
                        return tree
        # if you go through all transitions and they all reject, the string is rejected
        if next_level: frontier.append(next_level)

    print(f"Transitions Simulated: {sum([len(level) for level in tree])}")
    if len(tree) == 1:
        print(f'String rejected in 1 step')
    else:
        print(f'String rejected in {len(tree)} steps')
    return tree


def main(args=sys.argv[1:]):
    # Make sure user gave enough arguments
    if not args or len(args) < 2:
        usage(1)

    # Check to see if file exists
    TM_file = args[0]
    if not os.path.isfile(TM_file):
        print("File does not exist!")
        usage(1)

    # Build your turing machine and output info
    TM = build_TM(TM_file)
    TM.dump()

    input_string = args[1] + '_' if '_' not in args[1] else args[1]
    print(f'Input String: {input_string[:-1]}')

    try:
        step_limit = int(args[2])
    except IndexError:
        step_limit = 500

    # Start trace
    turing_machine_BFS(TM, input_string, step_limit)

if __name__ == "__main__":
    main()