"""
Cat Trap Algorithms

This is the relevant code for the LinkedIn Learning Course 
AI Algorithms for Game Design with Python, by Eduardo Corpeño

For the GUI, this code uses the Cat Trap UI VSCode extension
included in the extensions folder.
"""

import random
import copy
import time
import numpy as np

# Constants
CAT_TILE = 6
BLOCKED_TILE = 1
EMPTY_TILE = 0
LAST_CALL_MS = 1
VERBOSE = True

class InvalidMove(ValueError):
    pass

class CatTrapGame:
    """
    Represents a Cat Trap game state. Includes methods for initializing the game board, 
    managing game state, and selecting moves for the cat using different algorithms.
    """

    def __init__(self, size):
        self.cat_row = size // 2
        self.cat_col = size // 2
        self.size = size
        self.hexgrid = np.full((size, size), EMPTY_TILE)
        self.hexgrid[self.cat_row, self.cat_col] = CAT_TILE
        self.deadline = 0
        self.terminated = False
        self.start_time = time.time()
        self.eval_function = CatEvaluationFunction()
        self.reached_max_depth = False 
        self.max_depth = float('inf')

    def initialize_random_hexgrid(self):
        """Randomly initialize blocked hexgrid."""
        num_blocks = random.randint(round(0.067 * (self.size**2)), round(0.13 * (self.size**2)))
        count = 0
        self.hexgrid[self.cat_row, self.cat_col] = CAT_TILE

        while count < num_blocks:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            if self.hexgrid[r, c] == EMPTY_TILE:
                self.hexgrid[r, c] = BLOCKED_TILE
                count += 1    
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.pretty_print_hexgrid()

    def set_hexgrid(self, hexgrid):
        """Copy incoming hexgrid."""
        self.hexgrid = hexgrid
        self.cat_row, self.cat_col = tuple(np.argwhere(self.hexgrid == CAT_TILE)[0])  # Find the cat position  
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.pretty_print_hexgrid()
   
    def block_tile(self, r, c):
        self.hexgrid[r, c] = BLOCKED_TILE

    def unblock_tile(self, r, c):
        self.hexgrid[r, c] = EMPTY_TILE

    def place_cat(self, r, c):
        self.hexgrid[r, c] = CAT_TILE
        self.cat_row = r
        self.cat_col = c

    def move_cat(self, r, c):
        self.hexgrid[self.cat_row, self.cat_col] = EMPTY_TILE  # Clear previous cat position
        self.place_cat(r, c)

    # ===================== Intelligent Agents =====================
    """
    Intelligent Agents for the Cat Trap game. These agents take the game state and the
    cat's position as inputs and return the new position of the cat or indicate a failure.

    Available options:
      - random_cat: A random move for the cat.
      - alpha_beta: Use Alpha-Beta Pruning.
      - depth_limited: Use Depth-Limited Search with a specified maximum depth.
      - iterative_deepening: Use Iterative Deepening with an allotted time.
      - use_minimax: Use the Minimax algorithm.

    If none of these options are selected, no intelligent behavior is applied.
    """

    def select_cat_move(self, random_cat, alpha_beta, depth_limited, minimax, max_depth, iterative_deepening, allotted_time):
        """Select a move for the cat based on the chosen algorithm."""
        self.reached_max_depth = False 
        self.start_time = time.time()
        self.deadline = self.start_time + allotted_time 
        self.terminated = False
        self.max_depth = float('inf') 

        if VERBOSE:
            print('\n======= NEW MOVE =======')

        if random_cat:
            move = self.random_cat_move() 
        elif minimax:
            # Select a move using the Minimax algorithm.
            move, _ = self.alpha_beta() if alpha_beta else self.minimax()   
        elif depth_limited:
            # Select a move using Depth-Limited Search with optional Alpha-Beta pruning.
            self.max_depth = max_depth
            move, _ = self.alpha_beta() if alpha_beta else self.minimax()
        elif iterative_deepening:
            # Select a move using the Iterative Deepening algorithm.
            move, _ = self.iterative_deepening(use_alpha_beta = alpha_beta)
        else:
            move = None

        elapsed_time = (time.time() - self.start_time) * 1000
        if VERBOSE:
            print(f'Elapsed time: {elapsed_time:.3f}ms ')
            print(f'New cat coordinates: {move}')
            temp = copy.deepcopy(self)
            temp.move_cat(move[0], move[1])
            temp.pretty_print_hexgrid()
        return move

    def random_cat_move(self):
        """Randomly select a move for the cat."""
        moves = self.get_valid_moves()
        if VERBOSE:
            print(f'Moves: {moves}')  # Available directions for the next move: 'E', 'W', 'SE', 'SW', 'NE', 'NW'
        if moves:
            direction = random.choice(moves)
            return self.get_target_position(self.cat_row, self.cat_col, direction)
        return [self.cat_row, self.cat_col]
    
    def get_valid_moves(self):
        """
        Get a list of valid moves for the cat.
        """
        hexgrid, r, c = self.hexgrid, self.cat_row, self.cat_col
        size = self.size
        moves = []
        # Check possible directions for the next move: 'E', 'W', 'SE', 'SW', 'NE', 'NW'
        if c < size - 1 and hexgrid[r][c + 1] == EMPTY_TILE:
            moves.append('E')
        if c > 0 and hexgrid[r][c - 1] == EMPTY_TILE:
            moves.append('W')

        if r % 2 == 0:
            if r > 0 and c < size and hexgrid[r - 1][c] == EMPTY_TILE:
                moves.append('NE')
            if r > 0 and c > 0 and hexgrid[r - 1][c - 1] == EMPTY_TILE:
                moves.append('NW')
            if r < size - 1 and c < size and hexgrid[r + 1][c] == EMPTY_TILE:
                moves.append('SE')
            if r < size - 1 and c > 0 and hexgrid[r + 1][c - 1] == EMPTY_TILE:
                moves.append('SW')
        else:
            if r > 0 and c < size - 1 and hexgrid[r - 1][c + 1] == EMPTY_TILE:
                moves.append('NE')
            if r > 0 and c >= 0 and hexgrid[r - 1][c] == EMPTY_TILE:
                moves.append('NW')
            if r < size - 1 and c < size - 1 and hexgrid[r + 1][c + 1] == EMPTY_TILE:
                moves.append('SE')
            if r < size - 1 and c > 0 and hexgrid[r + 1][c] == EMPTY_TILE:
                moves.append('SW')
        return moves

    def get_target_position(self, r, c, direction):
        """
        Get the target position based on the current position and direction.
        """
        target = [r, c]
        if direction == 'E':
            target = [r, c + 1]
        elif direction == 'W':
            target = [r, c - 1]
        elif direction == 'NE':
            target = [r - 1, c] if r % 2 == 0 else [r - 1, c + 1]
        elif direction == 'NW':
            target = [r - 1, c - 1] if r % 2 == 0 else [r - 1, c]
        elif direction == 'SE':
            target = [r + 1, c] if r % 2 == 0 else [r + 1, c + 1]
        elif direction == 'SW':
            target = [r + 1, c - 1] if r % 2 == 0 else [r + 1, c]
        return target

    def utility(self, num_moves, maximizing_player=True):
        """
        Calculate the utility of the current game state.
        """
        # Terminal cases
        if (
            self.cat_row == 0 or self.cat_row == self.size - 1 or
            self.cat_col == 0 or self.cat_col == self.size - 1
        ):
            return float(100)
        
        # Only the cat can run out of moves
        if num_moves == 0: 
            return float(-100)

        # Use the evaluation function
        # Evaluation function options: 'moves', 'custom', 'proximity'
        evaluation_function = 'proximity'

        if evaluation_function == 'moves':
            return self.eval_function.score_moves(self, maximizing_player)
        elif evaluation_function == 'proximity':
            return self.eval_function.score_proximity(self, maximizing_player)
        elif evaluation_function == 'custom':
            return self.eval_function.score_custom(self, maximizing_player)
        return 0

    def apply_move(self, move, maximizing_player):
        """
        Apply a move to the game state.
        """
        if self.hexgrid[move[0], move[1]] != EMPTY_TILE:
            print(f'Attempting to move to {move} = {self.hexgrid[move[0], move[1]]}')
            self.pretty_print_hexgrid()
            raise InvalidMove('Invalid Move!')

        if maximizing_player:
            self.hexgrid[move[0], move[1]] = BLOCKED_TILE
        else:
            self.hexgrid[move[0], move[1]] = CAT_TILE  # Place the cat
            self.hexgrid[self.cat_row, self.cat_col] = EMPTY_TILE  # Remove the old cat
            self.cat_row, self.cat_col = move

    def max_value(self, upper_game, move, maximizing_player, depth):
        """
        Calculate the maximum value for the current game state in the minimax algorithm.
        """
        if self.time_left() < LAST_CALL_MS:
            self.terminated = True
            return [-1, -1], 0

        game = copy.deepcopy(upper_game)
        if move != [-1, -1]:
            maximizing_player = not maximizing_player
            game.apply_move(move, maximizing_player)
        
        legal_moves = game.get_valid_moves()  # Available directions: 'E', 'W', 'SE', 'SW', 'NE', 'NW'
        if not legal_moves or depth == self.max_depth:
            if depth == self.max_depth:
                self.reached_max_depth = True  
            return [self.cat_row, self.cat_col], (game.size**2 - depth) * game.utility(len(legal_moves), maximizing_player)
        
        best_value = float('-inf')
        best_move = game.get_target_position(game.cat_row, game.cat_col, legal_moves[0])
        for direction in legal_moves:
            target_pos = game.get_target_position(game.cat_row, game.cat_col, direction)
            value = self.min_value(game, target_pos, maximizing_player, depth + 1)

            if self.terminated:
                return [-1, -1], 0
            
            if value > best_value:
                best_value = value
                best_move = target_pos
  
        return best_move, best_value

    def min_value(self, upper_game, move, maximizing_player, depth):
        """
        Calculate the minimum value for the current game state in the minimax algorithm.

        Unlike max_value, min_value does not iterate over specific directions ('E', 'W', etc.).
        Instead, it examines every possible free tile on the board. This simplifies implementation
        for moves like blocking hexgrid, where legal positions are any unoccupied hexgrid, not directional.
        """
        if self.time_left() < LAST_CALL_MS:
            self.terminated = True
            return 0

        game = copy.deepcopy(upper_game)
        maximizing_player = not maximizing_player
        game.apply_move(move, maximizing_player)

        # Check if terminal state or depth limit is reached
        if depth == self.max_depth or (
            game.cat_row == 0 or game.cat_row == self.size - 1 or
            game.cat_col == 0 or game.cat_col == self.size - 1
        ):
            if depth == self.max_depth:
                self.reached_max_depth = True
            
            return (game.size**2 - depth) * game.utility(1, maximizing_player)
        
        best_value = float('inf')

        # Iterate through all legal moves for the player (empty tiles)
        legal_moves = [list(coord) for coord in np.argwhere(game.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            _, value = self.max_value(game, move, maximizing_player, depth + 1)
            best_value = min(best_value, value)

            if self.terminated:
                return 0
        
        return best_value

    def minimax(self, maximizing_player=True):
        """
        Perform the Minimax algorithm to determine the best move.
        """
        best_move, best_value = self.max_value(self, [-1, -1], maximizing_player, depth=0)
        return best_move, best_value

    def time_left(self):
        """
        Calculate the time remaining before the deadline.
        """
        return (self.deadline - time.time()) * 1000

    def print_hexgrid(self):
        """
        Print the current state of the game board.
        """
        for r in range(0, self.size, 2):
            print(self.hexgrid[r])
            if r + 1 < self.size:
                print('', self.hexgrid[r + 1])
        print()
        return
    
    def pretty_print_hexgrid(self):
        """
        Print the current state of the game board using custom characters.

        Args:
            empty_tile_char (str): Character to represent an empty tile.
            block_tile_char (str): Character to represent a blocked tile.
            cat_tile_char (str): Character to represent the cat.
        """
        # Create a mapping for tile values to characters
        tile_map = {
            EMPTY_TILE: '⬡',
            BLOCKED_TILE: '⬢',
            CAT_TILE: '🐈'
        }

        for r in range(self.size):
            # Add a leading space for odd rows for staggered effect
            prefix = ' ' if r % 2 != 0 else ''
            # Convert each row using the tile map
            row_display = ' '.join(tile_map[cell] for cell in self.hexgrid[r])
            print(prefix + row_display)

        return

    def alpha_beta_max_value(self, upper_game, move, alpha, beta, maximizing_player, depth):
        """
        Calculate the maximum value for the current game state using Alpha-Beta pruning.
        """
        if self.time_left() < LAST_CALL_MS:
            self.terminated = True
            return [-1, -1], 0

        game = copy.deepcopy(upper_game)
        if move != [-1, -1]:
            maximizing_player = not maximizing_player
            game.apply_move(move, maximizing_player)

        legal_moves = game.get_valid_moves()  # Available directions: 'E', 'W', 'SE', 'SW', 'NE', 'NW'
        if not legal_moves or depth == self.max_depth:
            if depth == self.max_depth:
                self.reached_max_depth = True
            return [self.cat_row, self.cat_col], (game.size**2 - depth) * game.utility(len(legal_moves), maximizing_player)

        best_value = float('-inf')
        best_move = game.get_target_position(game.cat_row, game.cat_col, legal_moves[0])
        for direction in legal_moves:
            target_pos = game.get_target_position(game.cat_row, game.cat_col, direction)
            value = self.alpha_beta_min_value(game, target_pos, alpha, beta, maximizing_player, depth + 1)

            if self.terminated:
                return [-1, -1], 0
            
            if value > best_value:
                best_value = value
                best_move = target_pos

            if best_value >= beta:
                return best_move, best_value
            alpha = max(alpha, best_value)

        return best_move, best_value

    def alpha_beta_min_value(self, upper_game, move, alpha, beta, maximizing_player, depth):
        """
        Calculate the minimum value for the current game state using Alpha-Beta pruning.

        Unlike max_value, min_value does not iterate over specific directions ('E', 'W', etc.).
        Instead, it examines every possible free tile on the board. This simplifies implementation
        for moves like blocking hexgrid, where legal positions are any unoccupied hexgrid, not directional.
        """
        if self.time_left() < LAST_CALL_MS:
            self.terminated = True
            return 0

        game = copy.deepcopy(upper_game)
        maximizing_player = not maximizing_player
        game.apply_move(move, maximizing_player)

        # Check if terminal state or depth limit is reached
        if depth == self.max_depth or (
            game.cat_row == 0 or game.cat_row == self.size - 1 or
            game.cat_col == 0 or game.cat_col == self.size - 1
        ):
            if depth == self.max_depth:
                self.reached_max_depth = True
            return (game.size**2 - depth) * game.utility(1, maximizing_player)

        best_value = float('inf')

        # Iterate through all legal moves for the player (empty tiles)
        legal_moves = [list(coord) for coord in np.argwhere(game.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            _, value = self.alpha_beta_max_value(game, move, alpha, beta, maximizing_player, depth + 1)
            best_value = min(best_value, value)

            if self.terminated:
                return 0
            
            if best_value <= alpha:
                return best_value
            beta = min(beta, best_value)

        return best_value

    def alpha_beta(self, alpha=float('-inf'), beta=float('inf'), maximizing_player=True):
        """
        Perform the Alpha-Beta pruning algorithm to determine the best move.
        """
        best_move, best_value = self.alpha_beta_max_value(self, [-1, -1], alpha, beta, maximizing_player, depth=0)
        return best_move, best_value

    def iterative_deepening(self, use_alpha_beta):
        """
        Perform iterative deepening search with an option to use Alpha-Beta pruning.
        """
        best_depth = 0
        output_move, utility = [self.cat_row, self.cat_col], 0
        for depth in range(1, self.size**2):
            self.reached_max_depth = False
            self.max_depth = depth
            if use_alpha_beta:
                best_move, utility = self.alpha_beta()
            else:
                best_move, utility = self.minimax()

            if self.terminated:
                break
            else:
                output_move = best_move
                best_depth = depth
                elapsed_time = (time.time() - self.start_time) * 1000
                if VERBOSE:
                    print(f'Done with a tree of depth {depth} in {elapsed_time:.3f}ms')

                if not self.reached_max_depth:
                    break

        if VERBOSE:
            print('Depth reached:', best_depth)
        return output_move, utility

class CatEvaluationFunction:
    """
    Evaluation function class containing different scoring methods.
    """

    def score_moves(self, game, maximizing_player_turn=True):
        """
        Evaluate based on the number of valid moves available for the cat.
        """
        cat_moves = game.get_valid_moves()
        return len(cat_moves) if maximizing_player_turn else len(cat_moves) - 1

    def score_proximity(self, game, maximizing_player_turn=True):
        """
        Evaluate based on the proximity of the cat to the board edges.
        """
        distances = [100, 100]  # High initial distances
        cat_moves = game.get_valid_moves()
        for move in cat_moves:
            distance = 0
            r, c = game.cat_row, game.cat_col
            while True:
                distance += 1
                r, c = game.get_target_position(r, c, move)
                if r < 0 or r >= game.size or c < 0 or c >= game.size:
                    break
                if game.hexgrid[r, c] != EMPTY_TILE:
                    distance *= 5
                    break
            distances.append(distance)

        distances.sort()
        return game.size * 2 - (distances[0] if maximizing_player_turn else distances[1])

    def score_custom(self, game, maximizing_player_turn=True):
        """
        Placeholder for a custom evaluation function.
        """
        # Write your custom logic here
        return 1 if maximizing_player_turn else -1
