import BoardGenerator
import random
import copy
import queue


class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.height = board.height
        self.width = board.width
        self.countmineboard = copy.deepcopy(board.countmineboard)  # a matrix showing the number of nearby mines
        self.curboard = 0 * self.board.board - 2
        # -2 means unchecked nodes,-1 means we find a mine,other numbers from 0 to 8 means the number of nearby mines

        self.toExplore = queue.Queue()  # node to be explored
        self.explored_nodes = set()  # nodes have been explored
        self.cleared_nodes = set()  # store all cleared/safe nodes known so far
        self.mine = set()  # store already uncovered mines
        self.fail = False  # fail=True if and only if we step on a mine
        self.constraints = set()  # store all constraints
        self.chain = {}  # chain of influence
        self.initial_start = set()
        self.initial_chain()

    def solve(self):
        # firstly,pick a node randomly and explore it
        first_node = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
        self.toExplore.put(first_node)
        self.cleared_nodes.add(first_node)
        self.initial_start.add(first_node)

        print("This is the board that I need to solve")
        self.print_board(0)
        print("\n\n Start playing...")

        while True:
            if not self.toExplore.empty():
                get_node = self.toExplore.get()
                self.explore(get_node)
                print("The node I choose is: ", get_node)
                self.print_board(1)
                self.explored_nodes.add(get_node)
                self.update_constraints()
                self.handle_constraints()

                if self.fail:
                    print("*********game over! Terrible Guess*********")
                    self.print_board(0)
                    return False

                elif len(self.mine) == self.board.minenum:
                    if self.check():
                        print("\n  ************  well done!  ************  ")
                        self.print_board(0)
                        self.build_chain()
                        return True
                    else:
                        print("*********game over! Terrible Inference*********")
                        return False
            else:
                random_select_node = self.random_select()
                print("We are not able to infer further, we will choose a cell randomly!")
                print("The node that I choose is: ", random_select_node)
                self.initial_start.add(random_select_node)
                self.toExplore.put(random_select_node)
                self.cleared_nodes.add(random_select_node)

    def explore(self, node):
        if self.countmineboard[node[0]][node[1]] == -1:
            print('the node I randomly choose is: ',  node)
            print('Unfortunately, it is a mine!')
            self.fail = True
            return
        elif self.countmineboard[node[0]][node[1]] == 0:
            # all neighbouring nodes are safe
            self.curboard[node[0]][node[1]] = self.countmineboard[node[0]][node[1]]
            around_nodes = self.get_around(node)

            for _node in around_nodes:
                self.cleared_nodes.add(_node)
                self.toExplore.put(_node)

                # self.constraints.add(( tuple(_node), 0, tuple(node) ))

            self.chain[node] = around_nodes
        else: # it means the number of mines between 1 and 8
            self.curboard[node[0]][node[1]] = self.countmineboard[node[0]][node[1]]
            direction = [(1,0),(-1,0),(0,-1),(0,1),(1,1),(-1,-1),(1,-1),(-1,1)]
            uncovered_mine_num = 0
            i = node[0]
            j = node[1]
            for dir in direction:
                neighbour_node = (i + dir[0], j + dir[1])
                if self.is_valid(neighbour_node) and neighbour_node in self.mine:
                    uncovered_mine_num += 1

            covered_mine_num = self.countmineboard[node[0]][node[1]] - uncovered_mine_num
            around_nodes = self.get_around(node)
            chain = set()
            chain.add(node)
            if around_nodes:  # means, around nodes is not empty,
                self.constraints.add( (tuple(around_nodes), covered_mine_num, tuple(chain) ) )

    def update_constraints(self):
        #  update constraints by getting the difference of any two constraints
        change = True
        tempcons = set()
        while change:
            change = False
            for clue_1, num1, chain_1 in self.constraints:
                clue_1_set = set(clue_1)
                chain_1_set = set(chain_1)

                for clue_2, num2, chain_2 in self.constraints:
                    clue_2_set = set(clue_2)
                    chain_2_set = set(chain_2)

                    if clue_2_set.issubset(clue_1_set) and not clue_1_set == clue_2_set:
                        new_clue = clue_1_set - clue_2_set
                        # new_clue = tuple(sorted(list(clue_1_set - clue_2_set)))
                        new_num = num1 - num2
                        new_chain = chain_1_set.union(chain_2_set)

                        exist = False
                        for clue_3, num3, chain_3 in self.constraints:
                            clue_3_set = set(clue_3)
                            if clue_3_set == new_clue:
                                exist = True

                        if not exist:
                            change = True
                            tempcons.add( ( tuple(new_clue), new_num, tuple(new_chain) ) )

            for _cons in tempcons:
                self.constraints.add(_cons)

    def handle_constraints(self):
        temp_cons = self.constraints.copy()
        for clue, num, chain in temp_cons:
            if num == 0:
                for _node in set(clue):
                    if _node not in self.cleared_nodes:
                        self.cleared_nodes.add(_node)
                        self.toExplore.put(_node)

                        for parent in set(chain):
                            self.chain[parent].add(_node)

                self.constraints.remove((clue, num, chain))

            if num == len(set(clue)):
                for _node in set(clue):
                    if _node not in self.mine:
                        self.mine.add(_node)
                        self.curboard[_node[0]][_node[1]] = 9

                        for parent in set(chain):
                            self.chain[parent].add(_node)
                self.constraints.remove((clue, num, chain))

        # remove constrain whose clue are known so far
        updated_constraint = set()
        for clue, num, chain in self.constraints:
            clue_set = set(clue)
            temp = clue_set.copy()
            for _node in temp:
                if _node in self.cleared_nodes:
                    clue_set.remove(_node)
                if _node in self.mine:
                    clue_set.remove(_node)
                    num = num -1
            # if not num == 0:  # means that this clue is still useful
            if clue_set:
                updated_constraint.add( ( tuple(clue_set), num, chain ) )
        self.constraints = updated_constraint

    def random_select(self):
        while True:
            temp = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            if temp not in self.explored_nodes and temp not in self.mine:
                return temp

    def get_around(self,node):
        res = set()
        i = node[0]
        j = node[1]
        direction = [(1,0),(-1,0),(0,-1),(0,1),(1,1),(-1,-1),(1,-1),(-1,1)]
        for dir in direction:
            neighbour_node = (i + dir[0],j + dir[1])
            if self.is_valid(neighbour_node) \
                    and neighbour_node not in self.cleared_nodes and neighbour_node not in self.mine:
                res.add(neighbour_node)
        return res

    def is_valid(self,node):
        return 0 <= node[0] < self.height and 0 <= node[1] < self.width

    def build_chain(self):
        def print_infer(node):
            if self.chain[node]:
                for son in self.chain[node]:
                    print(node," -> ",son)
                for son in self.chain[node]:
                    print_infer(son)

        x = input("Do you want to see the Chain of Influence ? (y or n): ")
        if x == 'y':
            print("\nChain of Influence ")
            for initial_point in self.initial_start:
                print("\nThis is a randomly selected start point")
                print_infer(initial_point)

    def check(self):
        # to check if all mine that we infer are correct
        for node in self.mine:
            if not self.countmineboard[node[0]][node[1]] == -1:
                return False
        return True

    def initial_chain(self):
        for i in range(self.height):
            for j in range(self.width):
                self.chain[(i, j)] = set()

    def print_board(self, state):
        """
        :param state: 1: playing  0: show the hidden map
        :return:
        """
        if state == 1:
            print(" ________________________________")
            for i in range(self.height):
                print('|', end="  ")
                for j in range(self.width):
                    if self.curboard[i][j] == -2:
                        print('*', end="  ")
                    elif self.curboard[i][j] == 9:
                        print('M', end="  ")
                    else:
                        print(self.curboard[i][j], end="  ")
                print('|', end="")
                print()
            print(" ________________________________ ")
            print()

        if state == 0:
            print(" ________________________________")
            for i in range(self.height):
                print('|', end="  ")
                for j in range(self.width):
                    if self.countmineboard[i][j] == -1:
                        print('M', end="  ")
                    else:
                        print(self.countmineboard[i][j], end="  ")
                print('|', end="")
                print()
            print(" ________________________________")





if __name__ == "__main__":
    newboard = BoardGenerator.Board(10,10,0.2)
    solveboard = MineSweeper(newboard)
    solveboard.solve()
