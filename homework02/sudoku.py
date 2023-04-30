import pathlib
import random
import typing as tp

T = tp.TypeVar("T")


def read_sudoku(path: tp.Union[str, pathlib.Path]) -> tp.List[tp.List[str]]:
    """ Прочитать Судоку из указанного файла """
    path = pathlib.Path(path)
    with path.open() as f:
        puzzle = f.read()
    return create_grid(puzzle)


def create_grid(puzzle: str) -> tp.List[tp.List[str]]:
    digits = [c for c in puzzle if c in "123456789."]
    grid = group(digits, 9)
    return grid


def display(grid: tp.List[tp.List[str]]) -> None:
    """Вывод Судоку """
    width = 2
    line = "+".join(["-" * (width * 3)] * 3)
    for row in range(9):
        print(
            "".join(
                grid[row][col].center(width) + ("|" if str(col) in "25" else "") for col in range(9)
            )
        )
        if str(row) in "25":
            print(line)
    print()


def group(values: tp.List[T], n: int) -> tp.List[tp.List[T]]:
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов
    """
    answer = []
    for i in range(n):
        answer.append(values[i * n: (i + 1) * n])
    return answer

def get_row(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера строки, указанной в pos
    """
    row = pos[0]
    return grid[row]


def get_col(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера столбца, указанного в pos
    """
    col = pos[1]
    return [grid[row][col] for row in range(9)]


def get_block(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения из квадрата, в который попадает позиция pos
    """
    block_row = pos[0] // 3  # Integer division to determine the block's row
    block_col = pos[1] // 3  # Integer division to determine the block's column

    values = []
    for i in range(3):
        for j in range(3):
            value = grid[block_row * 3 + i][block_col * 3 + j]
            values.append(value)

    return values


def find_empty_positions(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.Tuple[int, int]]:
    """Найти первую свободную позицию в пазле
    """
    for i in range(9):
        for j in range(9):
            if grid[i][j] == '.':
                return i, j
    return None


def find_possible_values(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.Set[str]:
    """Вернуть множество возможных значения для указанной позиции
    """
    row_values = set(grid[pos[0]])
    col_values = set(grid[i][pos[1]] for i in range(9))
    block_values = set(
        grid[i][j]
        for i in range((pos[0] // 3) * 3, (pos[0] // 3) * 3 + 3)
        for j in range((pos[1] // 3) * 3, (pos[1] // 3) * 3 + 3)
    )
    all_values = set(str(i) for i in range(1, 10))
    return all_values - row_values - col_values - block_values


def solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    """ Решение пазла, заданного в grid """
    """ Как решать Судоку?
        1. Найти свободную позицию
        2. Найти все возможные значения, которые могут находиться на этой позиции
        3. Для каждого возможного значения:
            3.1. Поместить это значение на эту позицию
            3.2. Продолжить решать оставшуюся часть пазла

    >>> grid = read_sudoku('puzzle1.txt')
    >>> solve(grid)
    [['5', '3', '4', '6', '7', '8', '9', '1', '2'], ['6', '7', '2', '1', '9', '5', '3', '4', '8'], ['1', '9', '8', '3', '4', '2', '5', '6', '7'], ['8', '5', '9', '7', '6', '1', '4', '2', '3'], ['4', '2', '6', '8', '5', '3', '7', '9', '1'], ['7', '1', '3', '9', '2', '4', '8', '5', '6'], ['9', '6', '1', '5', '3', '7', '2', '8', '4'], ['2', '8', '7', '4', '1', '9', '6', '3', '5'], ['3', '4', '5', '2', '8', '6', '1', '7', '9']]
    """
    # Find an empty position
    empty_position = find_empty_positions(grid)

    # If there are no more empty positions, the puzzle is solved
    if empty_position is None:
        return grid

    row, col = empty_position

    # Find all possible values for the empty position
    possible_values = find_possible_values(grid, empty_position)

    # Try each possible value
    for value in possible_values:
        grid[row][col] = value

        # Recursively solve the remaining puzzle
        if solve(grid) is not None:
            return grid

        # If the current value leads to an invalid solution, backtrack
        grid[row][col] = '.'

    # If no solution is found, return None
    return None


def check_solution(solution: tp.List[tp.List[str]]) -> bool:
    """ Если решение solution верно, то вернуть True, в противном случае False """
    # TODO: Add doctests with bad puzzles
    for row in range(len(solution)):
        result = set(get_row(solution, (row, 0)))
        if result != set('123456789'):
            return False

    for col in range(len(solution)):
        result = set(get_col(solution, (0, col)))
        if result != set('123456789'):
            return False

    for row in range(0, len(solution) - 1, 3):
        for col in range(0, len(solution) - 1, 3):
            result = set(get_block(solution, (row, col)))
            if result != set('123456789'):
                return False

    return True


def generate_sudoku(N: int) -> tp.List[tp.List[str]]:
    """Генерация судоку заполненного на N элементов

    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    grid = solve([['.' for i in range(9)] for j in range(9)])
    N = 81 - N

    while N > 0:
        rand_i = random.randint(0, 8)
        rand_j = random.randint(0, 8)
        if grid[rand_i][rand_j] != '.':
            grid[rand_i][rand_j] = '.'
            N -= 1
    return grid


if __name__ == "__main__":
    for fname in ["puzzle1.txt", "puzzle2.txt", "puzzle3.txt"]:
        grid = read_sudoku(fname)
        display(grid)
        solution = solve(grid)
        if not solution:
            print(f"Puzzle {fname} can't be solved")
        else:
            display(solution)
