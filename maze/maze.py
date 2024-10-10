
import sys

# Class representing a node in the search tree
class Node():
    def __init__(self, state, parent, action):
        # The state of the node (position in the maze)
        self.state = state
        # The parent node leading to this node
        self.parent = parent
        # The action taken to reach this node
        self.action = action

# Base class for managing the frontier (stack or queue)
class Frontier():
    def __init__(self):
        # List to store nodes in the frontier
        self.frontier = []
        # Set to quickly check if a state is already in the frontier
        self.frontier_states = set()

    # Add a node to the frontier
    def add(self, node):
        self.frontier.append(node)
        self.frontier_states.add(node.state)

    # Check if a given state is in the frontier
    def contains_state(self, state):
        return state in self.frontier_states

    # Check if the frontier is empty
    def empty(self):
        return len(self.frontier) == 0

# Stack-based frontier for depth-first search
class StackFrontier(Frontier):
    
    # Remove and return the last node (LIFO)
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        node = self.frontier.pop()
        self.frontier_states.remove(node.state)
        return node

# Queue-based frontier for breadth-first search
class QueueFrontier(Frontier):

    # Remove and return the first node (FIFO)
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]  # Remove the first element
            return node

# Class representing the maze
class Maze():

    def __init__(self, filename, use_queue):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate maze to ensure it has one start ('A') and one goal ('B')
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze from the file
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Initialize a 2D list to track walls (True for wall, False for empty space)
        self.walls = []  # True = Wall, False = Open space
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        # Start position
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        # Goal position
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        # Empty space
                        row.append(False)
                    else:
                        # Wall
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        # Solution will be set when maze is solved
        self.solution = None

    # Print the maze with solution path if it exists
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")  # Wall
                elif (i, j) == self.start:
                    print("A", end="")  # Start point
                elif (i, j) == self.goal:
                    print("B", end="")  # Goal point
                elif solution is not None and (i, j) in solution:
                    print("*", end="")  # Solution path
                else:
                    print(" ", end="")  # Empty space
            print()
        print()

    # Return neighboring positions (up, down, left, right) that are not blocked by walls
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            # Ensure the neighbor is within maze bounds and not a wall
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    # Solve the maze using DFS (stack) or BFS (queue)
    def solve(self, use_queue=False):
        """Finds a solution to maze, if one exists."""

        # Track the number of states explored
        self.num_explored = 0

        # Initialize the frontier with the start node
        start = Node(state=self.start, parent=None, action=None)

        # Choose queue for BFS or stack for DFS based on input
        if use_queue:
            frontier = QueueFrontier()
        else:
            frontier = StackFrontier()
        frontier.add(start)

        # Initialize the explored set to track visited nodes
        self.explored = set()

        # Loop until solution is found
        while True:

            # If no nodes left to explore, there is no solution
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If the goal is reached, construct the solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark the node as explored
            self.explored.add(node.state)

            # Add neighbors to the frontier if not already explored or in the frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    # Generate an image of the maze with the solution and explored cells
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50  # Size of each cell in the image
        cell_border = 2  # Border size between cells

        # Create a blank canvas for the maze
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        # Draw the maze, solution, and explored states if specified
        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution path
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored cells
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw the cell on the image
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        # Save the image to a file
        img.save(filename)


# Ensure proper command line arguments are provided
if len(sys.argv) != 3:
    sys.exit("Usage: python maze.py maze.txt use_queue: False or True")

# Create a maze instance, print it, solve it, and output the solution image
m = Maze(sys.argv[1], sys.argv[2])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)
