
class GridCount:

    low_cones = 0
    low_cubes = 0

    mid_cones = 0
    mid_cubes = 0

    high_cones = 0
    high_cubes = 0

    def __init__(self, bonus_point):
        self.bonus_point = bonus_point

    def total_piece_count(self) -> int:
        return self.low_cones + self.low_cubes + \
               self.mid_cones + self.mid_cubes + \
               self.high_cones + self.high_cubes

    def total_points(self) -> int:
        return self.low_cubes * (self.bonus_point + 2) + \
               self.low_cones * (self.bonus_point + 2) + \
               self.mid_cubes * (self.bonus_point + 3) + \
               self.mid_cones * (self.bonus_point + 3) + \
               self.high_cubes * (self.bonus_point + 5) + \
               self.high_cones * (self.bonus_point + 5)

    def __sub__(self, other):
        output = GridCount(self.bonus_point)

        output.low_cones = self.low_cones - other.low_cones
        output.low_cubes = self.low_cubes - other.low_cubes

        output.mid_cones = self.mid_cones - other.mid_cones
        output.mid_cubes = self.mid_cubes - other.mid_cubes

        output.high_cones = self.high_cones - other.high_cones
        output.high_cubes = self.high_cubes - other.high_cubes

        return output

    def __add__(self, other):
        output = GridCount(self.bonus_point)

        output.low_cones = self.low_cones + other.low_cones
        output.low_cubes = self.low_cubes + other.low_cubes

        output.mid_cones = self.mid_cones + other.mid_cones
        output.mid_cubes = self.mid_cubes + other.mid_cubes

        output.high_cones = self.high_cones + other.high_cones
        output.high_cubes = self.high_cubes + other.high_cubes

        return output

    def __repr__(self):
        return f"Low: {self.low_cones + self.low_cubes}, Mid: {self.mid_cones + self.mid_cubes} High: {self.high_cones + self.high_cubes}"
