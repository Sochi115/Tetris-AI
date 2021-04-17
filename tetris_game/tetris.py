import pygame
import copy
import time
import treenode_
import field_
import position_

from sys import stdin, stdout
from game_ import Game
from main import Main

class Bot:
    def __init__(self, a, b, c, d):
        self._game = Game()
        self._main = Main(self._game)

        # WEIGHTS
        self.aw = a
        self.bw = b
        self.cw = c
        self.dw = d
    
    def evaluate_pos(self, pos, bot, field, piece, a, b, c, d):
        list_aggr=[]
        """ a = -0.510066
        b = 0.760666
        c = -0.35663
        d = -0.184483 """
        for i in pos:
            aggr = bot.aggregate_height(i,bot, field, piece)
            comp = bot.complete_lines(i,bot, field, piece)
            hole = bot.holes(i,bot, field, piece)
            bump = bot.bumpiness(i,bot, field, piece)
            best_pos = (a*aggr)+1.5*(b*comp)+(c*hole)+(d*bump)
            list_aggr.append(best_pos)        
        max_value = max(list_aggr)
        max_value_index = list_aggr.index(max_value)
        best_pos = pos[max_value_index]
        return best_pos
            
    def aggregate_height(self, i,bot, field, piece):
        parent_field = copy.deepcopy(field.field)
        prot, px, py = i[0], i[1], i[2]
        block = field_.tetris_shapes[piece][prot]
        for j, row in enumerate(block):
            for i, val in enumerate(row):
                if val == 1:
                    val = 2
                    parent_field[j+py][i+px] += val
        col_cnt = []
        height_counter = 0
        total = 0
        for i in range(0,10):
            col = [x[i] for x in parent_field]
            for row, cell in enumerate(col):
                if bot._is_block(cell) and cell == 2:
                    height_counter += (20-row)
                    total += height_counter
                    break;
            col_cnt.append(height_counter)
            height_counter = 0
        return total
        
    def complete_lines(self, i,bot, field, piece):
        parent_field = copy.deepcopy(field.field)
        prot, px, py = i[0], i[1], i[2]
        block = field_.tetris_shapes[piece][prot]
        for j, row in enumerate(block):
            for i, val in enumerate(row):
                if val == 1:
                    val = 2
                    parent_field[j+py][i+px] += val
        complete_lines = 0
        for y in range(0,20):
            if all(map(lambda x: x == 2, parent_field[y])):
                complete_lines +=1
        return complete_lines
                
    def _is_block(self,cell):
        return cell != 0 

    def _is_empty(self,cell):
        return cell == 0
        
    def holes(self,i,bot, field, piece):
        parent_field = copy.deepcopy(field.field)
        prot, px, py = i[0], i[1], i[2]
        block = field_.tetris_shapes[piece][prot]
        for j, row in enumerate(block):
            for i, val in enumerate(row):
                if val == 1:
                    val = 2
                    parent_field[j+py][i+px] += val
        holes = []
        hole_counter = 0
        block_in_col = False
        for x in range(len(parent_field[0])):
            for y in range(len(parent_field)):
                if block_in_col and bot._is_empty(parent_field[y][x]):
                    holes.append((x,y))
                    hole_counter += 1
                elif bot._is_block(parent_field[y][x]) and parent_field[y][x] == 2:
                    block_in_col = True
            block_in_col = False
        return hole_counter
                
    def bumpiness(self, i,bot, field, piece):
        parent_field = copy.deepcopy(field.field)
        prot, px, py = i[0], i[1], i[2]
        block = field_.tetris_shapes[piece][prot]
        for j, row in enumerate(block):
            for i, val in enumerate(row):
                if val == 1:
                    val = 2
                    parent_field[j+py][i+px] += val
        col_cnt = []
        block_counter = 0
        for i in range(0,10):
            col = [x[i] for x in parent_field]
            for row, cell in enumerate(col):
                if bot._is_block(cell) and cell == 2:
                    block_counter += (20-row)
                    break;
            col_cnt.append(block_counter)
            block_counter = 0
        bumpiness = abs(col_cnt[0]-col_cnt[1]) + abs(col_cnt[1]-col_cnt[2]) + abs(col_cnt[2]-col_cnt[3])+abs(col_cnt[3]-col_cnt[4])+abs(col_cnt[4]-col_cnt[5])+abs(col_cnt[5]-col_cnt[6])+abs(col_cnt[6]-col_cnt[7])+abs(col_cnt[7]-col_cnt[8])+abs(col_cnt[8]-col_cnt[9])
        return bumpiness
    
    def get_moves(self,best_position, bot):
        moves = []
        parent_prot, parent_px = 0, 3
        best_prot = best_position[0]
        best_px = best_position[1]
        if parent_prot > best_prot:
            for i in range(best_prot, parent_prot):
                moves.append('turnleft')
        else:
            for i in range(parent_prot, best_prot):
                moves.append('turnright')
        if parent_px > best_px:
            for i in range(best_px, parent_px):
                moves.append('left')
        else:
            for i in range(parent_px, best_px):
                moves.append('right')
        moves.append('drop')
        return moves
        
    
    def build_tree2(self, field, piece):
        lst_pos, lst_pos2, lst_pos3 = [], [], []
        final_list = []
        list_ = copy.deepcopy(final_list)
        position = copy.deepcopy(treenode_.treenode.from_pos(field))
        if piece =='O':
            lst_pos.append((0,0,0))
        else:
            for i in range(0,4):
                position = treenode_.treenode.child(position, field, piece,'turnright')
                if position not in lst_pos:
                    lst_pos.append((position[0], position[1], position[2]))
        for i in lst_pos:
            if (piece =='O' and i[0] == 0):
                for j in range(0,8):
                    i = treenode_.treenode.child(i, field, piece, 'right')
                    lst_pos2.append((i[0], i[1], i[2]))
                field.px=0
            elif (piece =='I' and i[0] == 0) or (piece == 'I' and i[0] == 2):
                for j in range(0,6):
                    i = treenode_.treenode.child(i, field, piece,'right')
                    lst_pos2.append((i[0], i[1], i[2]))
                field.px = 0
            elif (piece =='I' and i[0] == 1):
                for j in range(0,7):
                    i = treenode_.treenode.child(i,field, piece, 'right')
                    lst_pos2.append((i[0], i[1], i[2]))
                field.px=0
            elif (i[0] == 3):
                for j in range(0,8):
                    i = treenode_.treenode.child(i,field, piece, 'right')
                    lst_pos2.append((i[0], i[1], i[2]))
                field.px=0   
            else:
                for j in range(0,7):
                    i = treenode_.treenode.child(i,field, piece, 'right')
                    lst_pos2.append((i[0], i[1], i[2]))
                field.px=0
        lst_pos.extend(lst_pos2)  
        for position in lst_pos:
            while treenode_.treenode.is_legal(position,field, piece) == False:
                position = treenode_.treenode.child(position, field, piece, 'down')
                lst_pos3.append(position)
            del lst_pos3[-1]
            field.prot, field.px, field.py = 0, 0, 0
            final_list.append(lst_pos3[-1])
        final_list = sorted(final_list, reverse=False)
        list_ = final_list
        final_list = []
        return list_

    def run(self):
        while not stdin.closed:
            try:
                line = stdin.readline().strip()
                if len(line) == 0:
                    continue
                moves = self.interpret(line)
                if moves:
                    self.sendMoves(moves)
            except EOFError:
                return
   
    def interpret(self, line):
        if line.startswith('action'):
            bot=Bot() 
            moves=bot.build_tree2(self._game.me.field,self._game.currentPiece)            
            best_position= bot.evaluate_pos(moves,bot, self._game.me.field, self._game.currentPiece)
            best_prot=best_position[0]
            best_px=best_position[1]
            best_py=best_position[2]
            if self._game.currentPiece=='O':
                best_position=best_prot, best_px-1, best_py
            action_moves=bot.get_moves(best_position, bot)
            return action_moves
        else:
            self._main.parse(line)

    @staticmethod
    def sendMoves(moves):
        stdout.write(','.join(moves) + '\n')
        stdout.flush()


class Simulate():
    def __init__(self):
        self.cnt_moves = 0
        self.cnt_cleared_lines = 0
        self.round = 0
        self.score = 0
        self.combo = 0
    
    def generate(self,a,b,c,d):
        bot = Bot(a,b,c,d)
        field = copy.deepcopy(field_.pos.field)
        while True:
            try:
                moves = bot.build_tree2(field_.pos, field_.pos.currentPiece)
                best_position = bot.evaluate_pos(moves, bot, field_.pos, field_.pos.currentPiece, a, b, c, d)
                action_moves = bot.get_moves(best_position, bot)
                move=position_.Position(field_.pos, field_.pos.currentPiece, field_.pos.nextPiece)
                field_.pos.prot=best_position[0]
                clears=move.from_tree_node(best_position)
                if clears==1:
                    self.score+=1
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==2:
                    self.score+=3
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==3:
                    self.score+=6
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==4:
                    self.score+=10
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                else:
                    self.combo=0
                
                field_.pos.currentPiece=move.nextPiece
                field_.pos.nextPiece=field_.pos.getNextPiece() 
                self.cnt_moves+=1
                self.cnt_cleared_lines+=clears
                self.round+=1
                
            except IndexError:
                field_.pos.field=field
                return self.cnt_moves, self.cnt_cleared_lines
                

    def runGame(self,a,b,c,d):
        bot = Bot(a,b,c,d)
        field = copy.deepcopy(field_.pos.field)

        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (128, 128, 128)

        # Initialise Pygame
        pygame.init()

        size = (400,500)
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption("Tetris")

        clock = pygame.time.Clock()
        fps = 25

        done = False
        while not done:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            try:
                print ('Current piece: ', field_.pos.currentPiece)
                print('Next piece: ', field_.pos.nextPiece)
                moves = bot.build_tree2(field_.pos, field_.pos.currentPiece)
                best_position = bot.evaluate_pos(moves, bot, field_.pos, field_.pos.currentPiece, a, b, c, d)
                action_moves = bot.get_moves(best_position, bot)
                move=position_.Position(field_.pos, field_.pos.currentPiece, field_.pos.nextPiece)
                field_.pos.prot=best_position[0]
                clears=move.from_tree_node(best_position)
                if clears==1:
                    self.score+=1
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==2:
                    self.score+=3
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==3:
                    self.score+=6
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                elif clears==4:
                    self.score+=10
                    if self.combo>0:
                        self.combo+=1
                        self.score=self.score+self.combo-1
                    else:
                        self.combo+=1
                else:
                    self.combo=0
                
                screen.fill(BLACK)

                for i in range(20):
                    for j in range(10):
                        pygame.draw.rect(screen, WHITE, [100 + 20 *j, 60 + 20*i, 20, 20], 1)
                        if field_.pos.field[i][j] == 3:
                            pygame.draw.rect(screen, (255,0,0) , [100 + 20 *j + 1, 60 + 20*i + 1, 20 - 2, 20 - 1])
                        elif field_.pos.field[i][j] > 0:
                            pygame.draw.rect(screen, (0,255,0) , [100 + 20 *j + 1, 60 + 20*i + 1, 20 - 2, 20 - 1])
                
                font = pygame.font.SysFont('Calibri', 25, True, False)
                font1 = pygame.font.SysFont('Calibri', 65, True, False)
                text = font.render("Score: " + str(self.score)+ " Current: " + field_.pos.currentPiece + " Next: " + field_.pos.nextPiece , True, WHITE)
                text_game_over = font1.render("Game Over", True, (255, 125, 0))
                text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

                screen.blit(text, [0, 0])
                
                field_.pos.print_pos()
                print ('Best position', best_position, 'Action moves', action_moves)
                field_.pos.currentPiece=move.nextPiece
                field_.pos.nextPiece=field_.pos.getNextPiece() 
                self.cnt_moves+=1
                self.cnt_cleared_lines+=clears
                self.round+=1
                """ if self.round==15:
                    field_.pos.insert_row()
                    self.round=0
                else:
                    pass """
                print ('score', self.score)
                print ('combo', self.combo)
                pygame.display.flip()
                clock.tick(fps)
            except IndexError:
                field_.pos.field=field
                
                screen.blit(text_game_over, [20, 200])
                screen.blit(text_game_over1, [25, 265])
                return self.cnt_moves, self.cnt_cleared_lines
                
            time.sleep(1)
pygame.quit()
