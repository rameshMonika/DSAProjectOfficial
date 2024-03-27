import random

def fitness(data, target):
    return sum([abs(x - target) for x in data])

def mutate(parent):
    index = random.randint(0, len(parent) - 1)
    child = list(parent)
    child[index] = random.randint(min(parent), max(parent))
    return child

def genetic_algorithm(data, target):
    best_individual = data
    best_fitness = fitness(data, target)

    for _ in range(1000):  # Number of generations
        child = mutate(best_individual)
        child_fitness = fitness(child, target)

        if child_fitness < best_fitness:
            best_individual = child
            best_fitness = child_fitness

    return best_individual

# Example usage:
data = [random.randint(0, 100) for _ in range(10)]
target = 50
filtered_data = genetic_algorithm(data, target)

print("Original data:", data)
print("Target:", target)
print("Filtered data:", filtered_data)