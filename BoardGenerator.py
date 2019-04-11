# coding: utf-8

import random
import numpy as np


class Board:
    def __init__(self,height,width,prob):
        """
        Create a new board
        param height(int): the height of board
        param width(int): the width of board

        param prob(double): the probability the cell to be occupied, which means a mine
        param minenum(int):the number of mines

        """
        self.height = height
        self.width = width

        self.prob = prob

        # check if prob between 0 and 1
        if prob < 0 or prob > 1:
            raise ValueError('prob should between 0 and 1')

        # create a uniform distribution matrix
        self.board = np.random.uniform(low=0,high=1,size=[height,width])
        # generate board matrix, '0':empty '-1':mines
        self.board = -(self.board < prob).astype(int)
        self.countmineboard = self.board.copy()
        self.minenum = len(self.board[(self.board == -1)])
        self.count_mines()

    def count_mines(self):
        # return a matrix showing the number of mines near every cell
        direction = [(1,0),(-1,0),(0,-1),(0,1),(1,1),(-1,-1),(1,-1),(-1,1)]
        for i in range(self.height):
            for j in range(self.width):
                num = 0
                if (self.board[i][j] == -1):
                    continue  # it's a mine so we don't need to count

                else:
                    for dir in direction:
                        neighbournode = (i + dir[0],j + dir[1])
                        if self.isvalid(neighbournode):
                            if self.board[neighbournode[0]][neighbournode[1]] == -1:
                                num += 1
                    self.countmineboard[i][j] = num

    def isvalid(self,node):
        return 0 <= node[0] < self.height and 0 <= node[1] < self.width

    def print_board(self):
        # print the board as a matrix '0':empty '-1':mines
        print(self.board)

    def get_board(self):
        # return a board(height by width matrix) with mines
        return self.board
