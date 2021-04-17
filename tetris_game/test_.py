from tetris import Simulate
import random

class Test():

    def __init__(self):
        self.avg_moves = 0
        self.avg_cl_lines = 0
        self.genes =[]
        

    def process(self):
        generations = 15
        population = 200
        genes = []
        scores = []
        fittest = []
        for generation in range(generations):
            offsprings = []
            newGenes = []
            avgFitness = 0

            print(f"Generation {generation}")
            if generation > 0:
                #print(genes)
                genes = sorted(genes, key = lambda x:x[1], reverse= True)
                fittest.append(genes[0])
                print(fittest)

                # New generation
                for i in range(60):
                    tournament = []
                    for j in range (20):
                        temp = random.randint(0,population - 1)
                        while temp in tournament:
                            temp = random.randint(0,population - 1)
                        tournament.append(genes[temp])

                    tournament = sorted(tournament, key = lambda x:x[1], reverse = True)
                    g1 = tournament[0]
                    g2 = tournament[1]
                    offsprings.append((self.crossover(g1[0],g2[0]), 0))

                # Sort Genes
                #genes = sorted(genes, key = lambda x:x[1], reverse = True)
                for i in range(140):
                    newGenes.append(genes[i])
                newGenes.extend(offsprings)

                genes = []

                for i in range(population):
                    if i%50==0:
                        print(f"G {generation} p {i}")
                    gene = newGenes[i]
                    parameters = gene[0]
                    a = parameters[0]
                    b = parameters[1]
                    c = parameters[2]
                    d = parameters[3]
                    avg_lines = 0
                    for games in range(25):
                        result = Simulate().generate(a,b,c,d)
                        avg_lines += result[1]
                    avg_lines /= 25
                    avgFitness += avg_lines
                    genes.append(([a,b,c,d], avg_lines))
                
                avgFitness /= population

                scores.append(avgFitness)
                print(f"Average fitness for generation {generation} = {avgFitness}")
                print(f"\nScores: {scores}")    
            else:
                for i in range(population):
                    a = random.uniform(0,1)
                    b = random.uniform(0,1)
                    c = random.uniform(0,1)
                    d = random.uniform(0,1)

                    a *= -1
                    c *= -1
                    d *= -1
                    if i % 50 == 0:
                        print(i)
                    avg_lines = 0
                    for games in range(25):
                        result = Simulate().generate(a,b,c,d)
                        avg_lines += result[1]
                    avg_lines /= 25
                    avgFitness += avg_lines
                    genes.append(([a,b,c,d], avg_lines))

                avgFitness /= population
                scores.append(avgFitness)
                print(f"Average fitness for generation {generation} = {avgFitness}")   
        
        genes = sorted(genes, key = lambda x:x[1], reverse = True)
        print(scores)

        print(fittest)
        alpha = genes[0]
        return alpha[0]

    """ 
    def selectOne(self, genes):
        maxVal = sum([gene[1] for gene in genes]) """

    def crossover(self, gene1, gene2):
        offspring = [0,0,0,0]
        r = random.randint(0,2)
        for i in range (0,4):
            if i == r or i == r+1:
                offspring[i] = gene1[i]
            else:
                offspring[i] = gene2[i]

        # Mutation
        mutation_rate = random.uniform(0,1)
        if mutation_rate < 0.15:
            parameter = random.randint(0,3)
            operator = random.randint(0,1)
            amount = random.uniform(0,0.2)
            if operator == 0:
                offspring[parameter] += amount
            else:
                offspring[parameter] -= amount

        return offspring

    def play(self, n, a, b, c, d):
        for game in range(n):
            print ('GAME: ', game)
            result = Simulate().runGame(a,b,c,d)
            self.avg_moves += result[0]
            self.avg_cl_lines += result[1]
        self.avg_moves = self.avg_moves / n
        print ("NUMBER OF GAMES PLAYED: ", n)
        print ('Average number of moves: ', self.avg_moves)
        self.avg_cl_lines = self.avg_cl_lines / n
        print ('Average number of cleared lines: ', self.avg_cl_lines)


play_tetris = Test()
""" print("Running Generations")
parameters = play_tetris.process()
print("After 15 generations, parameters are: ")
print(parameters) """


n = int(input("Enter a number n: "))

#play_tetris.play(n, -0.51006, 0.760666, -0.35663, -0.184483)

#play_tetris.play(n, -0.24487121687555247,  0.44440096026965537, -0.3018285610321827, -0.1329351947363867)

#play_tetris.play(n, -0.7578143479657238, 0.827682680976591, -0.3774429939727665, -0.9059985051713307)

#play_tetris.play(n, -0.2312979489902306,  0.9368774336393004, -0.13235948156660815, -0.14670037477123077)
#play_tetris.play(n, -0.22978719948938764, 0.832143761454859, -0.06613042355292809, -0.13628315104715827)

play_tetris.play(n,-0.06025077652566957, 0.6393614141284109, -0.18897256702496124, -0.11628880049904478)
#, 27.48)


