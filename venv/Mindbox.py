# Импортируем библиотеку math
import math


class GeometryCalculator:
    @staticmethod
    # Функция подсчета площади круга
    def circle_area(radius):
        if radius < 0:
            raise ValueError("Радиус не может быть отрицательным")
        return math.pi * radius ** 2

    @staticmethod
    # Функция подсчета площади треугольника
    def triangle_area(side1, side2, side3):
        if side1 <= 0 or side2 <= 0 or side3 <= 0:
            raise ValueError("Длины сторон должны быть положительными числами")
        s = (side1 + side2 + side3) / 2
        area = math.sqrt(s * (s - side1) * (s - side2) * (s - side3))
        return area

    @staticmethod
    # Функция возвращающая True если треугольник прямоугольный
    def is_right_triangle(side1, side2, side3):
        sides = [side1, side2, side3]
        sides.sort()
        return math.isclose(sides[0] ** 2 + sides[1] ** 2, sides[2] ** 2, rel_tol=1e-9)


# Пример использования:
if __name__ == "__main__":
    calc = GeometryCalculator()

    radius = 5.0
    circle_area = calc.circle_area(radius)
    print(f"Площадь круга с радиусом {radius} равна {circle_area:.2f}")

    side1 = 3.0
    side2 = 4.0
    side3 = 5.0
    triangle_area = calc.triangle_area(side1, side2, side3)
    print(f"Площадь треугольника с сторонами {side1}, {side2}, {side3} равна {triangle_area:.2f}")

    if calc.is_right_triangle(side1, side2, side3):
        print("Треугольник является прямоугольным.")
    else:
        print("Треугольник не является прямоугольным.")
