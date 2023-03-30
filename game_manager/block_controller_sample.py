#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import MINYEAR, datetime
from opcode import haslocal
from operator import index
import pprint
import copy
import numpy as np

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0
    HoldShapeDirectionRange = 0
    HoldShape_class = 0
    isExchangeHoldShape = 0
    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.


    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        #Hold
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]
        self.HoldShape_class = GameStatus["block_info"]["holdShape"]["class"]



        # search best nextMove -->
        strategy = None
        LatestEvalValue = -100000
        # search with current block Shape




        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            kizyun =len([i for i in self.board_backboard if i > 0])
            for x0 in range(x0Min,x0Max):
 
            
                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)

                    # evaluate board
                    EvalValue = self.calcEvaluationValueSample(board)
                    # update best move

                    if EvalValue > LatestEvalValue:
                        if kizyun <=40:
                            if x0==9or x0==10:
                               continue
                        strategy = (direction0, x0, 1, 1,"n")

                        LatestEvalValue = EvalValue


            if self.HoldShape_class == None:
                 print("===", datetime.now() - t1)
                 nextMove["strategy"]["direction"] = strategy[0]
                 nextMove["strategy"]["x"] = strategy[1]
                 nextMove["strategy"]["y_operation"] = strategy[2]
                 nextMove["strategy"]["y_moveblocknum"] = strategy[3]
                 nextMove["strategy"]["use_hold_function"]="y"
                 return  nextMove



            for direction1 in HoldShapeDirectionRange:

            # search with x range
                x0Min, x0Max = self.getSearchXRange(self.HoldShape_class, direction1)
                kizyun =len([i for i in self.board_backboard if i > 0])
                for x0 in range(x0Min,x0Max):

                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.HoldShape_class, direction1, x0)

                    # evaluate board
                    EvalValue = self.calcEvaluationValueSample(board)
                    # update best move

                    if EvalValue > LatestEvalValue:

                        strategy = (direction1, x0, 1, 1,"y")
                        LatestEvalValue = EvalValue



                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
        # search best nextMove <--

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        nextMove["strategy"]["use_hold_function"]=strategy[4]
        print(nextMove)
        print("###### SAMPLE CODE ######")

        return nextMove
        

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def exchangeholdShape(self):
        if self.holdShape == None:
            self.holdShape =self.CurrentShape_class
            self.createNewPiece()
            return False
        else:
            self.holdShape,self.CurrentShape_class = self.CurrentShape_class,self.holdShape
            Xmin,Xmax,Ymin,Ymax = self.NextShape_class.getBoundingOffsets(0)
            self.currentX = 5
            self.currentY = -Ymin
            self.currentDirection = 0
        return True

    def calcEvaluationValueSample(self, board):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height
        kaunnt = 0
        # evaluation paramters
        ## lines to be removed
        fullLines = -3
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        kizyun = 0
        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            kizyun =len([i for i in self.board_backboard if i > 0])
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 2:
                        nIsolatedBlocks += 1                 # update number of isolated blocks
                    if holeConfirm[x] > 3:
                        nIsolatedBlocks += 5
            if hasBlock == True and hasHole == False:
                # filled with block
                kaunnt +=1
                fullLines +=2
                fullLines *=1
                if kizyun>=100:
                    fullLines +=5
                if kizyun>=70:
                    fullLines +=2
                if kaunnt >=3:
                    fullLines +=20

                if kaunnt <3:
                    fullLines -=3
                if kizyun<=40:
                    fullLines -=10

            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)-3

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)


        # calc Evaluation Value
        score = 0
        score = score + fullLines * 3.0           # try to delete line 
        score = score - nHoles * 20.0               # try not to make hole
        score = score - nIsolatedBlocks * 20.0      # try not to make isolated block
        score = score - absDy * 1.0               # try to put block smoothly
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score


BLOCK_CONTROLLER_SAMPLE = Block_Controller()
