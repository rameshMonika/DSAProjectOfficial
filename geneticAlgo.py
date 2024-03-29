import random
import unittest

def genetic_algorithm(graph, origin, destination, max_distance, population_size=100, generations=500):
    # Initialize population with random routes
    population = [[origin] + random.sample(list(graph.keys()), len(graph) - 1) + [destination] for _ in range(population_size)]

    for _ in range(generations):
        # Calculate fitness of each individual in the population
        fitnesses = [calculate_fitness(individual, graph, max_distance) for individual in population]

        # Select individuals for reproduction
        parents = select_parents(population, fitnesses)

        # Create next generation through crossover and mutation
        population = reproduce(parents)

    # Return the individual with the highest fitness from the final generation
    return max(population, key=lambda individual: calculate_fitness(individual, graph, max_distance))

def calculate_fitness(route, graph, max_distance):
    total_distance = sum(graph[route[i]][route[i+1]] for i in range(len(route) - 1))
    return max_distance - total_distance if total_distance <= max_distance else 0

def select_parents(population, fitnesses):
    return random.choices(population, weights=fitnesses, k=len(population))

def reproduce(parents):
    next_generation = []
    for i in range(0, len(parents), 2):
        next_generation += crossover(parents[i], parents[i+1])
        next_generation[-2] = mutate(next_generation[-2])
        next_generation[-1] = mutate(next_generation[-1])
    return next_generation

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 2)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(route):
    i, j = random.sample(range(1, len(route) - 1), 2)
    route[i], route[j] = route[j], route[i]
    return route

class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        self.graph = {
            'A': {'B': 1, 'C': 3, 'D': 7},
            'B': {'A': 1, 'C': 1, 'D': 5},
            'C': {'A': 3, 'B': 1, 'D': 2},
            'D': {'A': 7, 'B': 5, 'C': 2}
        }

    def test_genetic_algorithm(self):
        route = genetic_algorithm(self.graph, 'A', 'D', 10)
        self.assertEqual(route[0], 'A')
        self.assertEqual(route[-1], 'D')
        total_distance = sum(self.graph[route[i]][route[i+1]] for i in range(len(route) - 1))
        self.assertLessEqual(total_distance, 10)

if __name__ == '__main__':
    unittest.main()