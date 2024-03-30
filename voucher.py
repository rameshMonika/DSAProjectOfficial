import heapq

# Define weights for discount percentage and number of passengers
weight_discount = 0.4
weight_passengers = 0.6

cached_scores = {}

# Function to calculate weighted score
def calculate_weighted_score(passengers, ticket_price, discount):
    # Check if the result is already cached
    if (passengers, ticket_price, discount) in cached_scores:
        return cached_scores[(passengers, ticket_price, discount)]
    
    # Calculate the weighted score
    weighted_score = (weight_discount * discount) + (weight_passengers * passengers)
    
    # Cache the result
    cached_scores[(passengers, ticket_price, discount)] = weighted_score
    
    return weighted_score

passengers = int(input("Enter number of passengers: "))
ticket_price = float(input("Enter ticket price: "))

def display_top_usable_vouchers(passengers, ticket_price, top_n=5):
    ranked_vouchers = []
    selected_vouchers = set()  
    for _, (p, tp, d) in enumerate(voucher_data):
        if p <= passengers and tp <= ticket_price:
            weighted_score = calculate_weighted_score(p, tp, d)
            heapq.heappush(ranked_vouchers, (-weighted_score, p, tp, d))
            ranked_vouchers.append((-weighted_score, p, tp, d))

    ranked_vouchers.sort()

    top_vouchers = []
    for _, (weighted_score, p, tp, d) in enumerate(ranked_vouchers):
        if len(top_vouchers) >= top_n:
            break  # Stop once we have found the desired number of top vouchers

        # Check if the voucher is already selected
        if (p, tp, d) not in selected_vouchers:
            savings = d / 100 * tp
            top_vouchers.append((p, tp, d, -weighted_score, savings))
            selected_vouchers.add((p, tp, d))

    return top_vouchers


voucher_data = [
    (3, 200, 10),   # Voucher 1
    (2, 150, 15),   # Voucher 2
    (5, 300, 20),   # Voucher 3
    (4, 250, 25),   # Voucher 4
    (3, 400, 10),   # Voucher 5
    (6, 350, 30),   # Voucher 6
    (2, 200, 20),   # Voucher 7
    (4, 450, 15),   # Voucher 8
    (7, 300, 25),   # Voucher 9
    (5, 350, 30),   # Voucher 10
    (2, 400, 10),   # Voucher 11
    (3, 250, 15),   # Voucher 12
    (4, 200, 25),   # Voucher 13
    (5, 450, 20),   # Voucher 14
    (3, 300, 10),   # Voucher 16
    (7, 400, 15),   # Voucher 17
    (4, 350, 20),   # Voucher 18
    (5, 250, 25),   # Voucher 19
    (6, 200, 30),   # Voucher 20
    (2, 300, 5),    # Voucher 21
    (3, 350, 25),   # Voucher 22
    (4, 200, 20),   # Voucher 23
    (5, 250, 15),   # Voucher 24
    (6, 400, 10),   # Voucher 25
    (3, 450, 30),   # Voucher 26
    (4, 300, 25),   # Voucher 27
    (5, 200, 20),   # Voucher 28
    (6, 350, 15),   # Voucher 29
    (2, 400, 10),   # Voucher 30
    (3, 250, 15),   # Voucher 31
    (4, 200, 25),   # Voucher 32
    (5, 450, 20),   # Voucher 33
    (3, 300, 10),   # Voucher 35
    (7, 400, 15),   # Voucher 36
    (4, 350, 20),   # Voucher 37
    (5, 250, 25),   # Voucher 38
    (6, 200, 30),   # Voucher 39
    (2, 300, 5),    # Voucher 40
    (3, 350, 25),   # Voucher 41
    (4, 200, 20),   # Voucher 42
    (5, 250, 15),   # Voucher 43
    (6, 400, 10),   # Voucher 44
    (3, 450, 30),   # Voucher 45
    (4, 300, 25),   # Voucher 46
    (5, 200, 20),   # Voucher 47
    (6, 350, 15),   # Voucher 48
    (2, 400, 10),   # Voucher 49
    (3, 250, 15),   # Voucher 50
    (4, 200, 25),   # Voucher 51
    (5, 450, 20),   # Voucher 52
    (3, 300, 10),   # Voucher 54
    (7, 400, 15),   # Voucher 55
    (4, 350, 20),   # Voucher 56
    (5, 250, 25),   # Voucher 57
    (6, 200, 30),   # Voucher 58
    (2, 300, 5),    # Voucher 59
    (3, 350, 25),   # Voucher 60
    (4, 200, 20),   # Voucher 61
    (5, 250, 15),   # Voucher 62
    (6, 400, 10),   # Voucher 63
    (3, 450, 30),   # Voucher 64
    (4, 300, 25),   # Voucher 65
    (5, 200, 20),   # Voucher 66
    (6, 350, 15),   # Voucher 67
    (2, 400, 10),   # Voucher 68
    (3, 250, 15),   # Voucher 69
    (4, 200, 25),   # Voucher 70
    (5, 450, 20),   # Voucher 71
    (6, 150, 30),   # Voucher 72
    (3, 300, 10),   # Voucher 73
    (7, 400, 15),   # Voucher 74
    (4, 350, 20),   # Voucher 75
    (5, 250, 25),   # Voucher 76
    (6, 200, 30),   # Voucher 77
    (2, 300, 5),    # Voucher 78
    (3, 350, 25),   # Voucher 79
    (4, 200, 20),   # Voucher 80
    (5, 250, 15),   # Voucher 81
    (6, 400, 10),   # Voucher 82
    (3, 450, 30),   # Voucher 83
    (4, 300, 25),   # Voucher 84
    (5, 200, 20),   # Voucher 85
    (6, 350, 15),   # Voucher 86
    (2, 400, 10),   # Voucher 87
    (3, 250, 15),   # Voucher 88
    (4, 200, 25),   # Voucher 89
    (5, 450, 20),   # Voucher 90
    (3, 300, 10),   # Voucher 92
    (7, 400, 15),   # Voucher 93
    (4, 350, 20),   # Voucher 94
    (5, 250, 25),   # Voucher 95
    (6, 200, 30),   # Voucher 96
    (2, 300, 5),    # Voucher 97
    (3, 350, 25),   # Voucher 98
    (4, 200, 20),   # Voucher 99
    (5, 250, 15),   # Voucher 100
   
]

voucher_data += [
    (6, 400, 10),   # Voucher 101
    (3, 450, 30),   # Voucher 102
    (4, 300, 25),   # Voucher 103
    (5, 200, 20),   # Voucher 104
    (6, 350, 15),   # Voucher 105
    (2, 400, 10),   # Voucher 106
    (3, 250, 15),   # Voucher 107
    (4, 200, 25),   # Voucher 108
    (5, 450, 20),   # Voucher 109
    (3, 300, 10),   # Voucher 111
    (7, 400, 15),   # Voucher 112
    (4, 350, 20),   # Voucher 113
    (5, 250, 25),   # Voucher 114
    (6, 200, 30),   # Voucher 115
    (2, 300, 5),    # Voucher 116
    (3, 350, 25),   # Voucher 117
    (4, 200, 20),   # Voucher 118
    (5, 250, 15),   # Voucher 119
    (6, 400, 10),   # Voucher 120
    (3, 450, 30),   # Voucher 121
    (4, 300, 25),   # Voucher 122
    (5, 200, 20),   # Voucher 123
    (6, 350, 15),   # Voucher 124
    (2, 400, 10),   # Voucher 125
    (3, 250, 15),   # Voucher 126
    (4, 200, 25),   # Voucher 127
    (5, 450, 20),   # Voucher 128
    (3, 300, 10),   # Voucher 130
    (7, 400, 15),   # Voucher 131
    (4, 350, 20),   # Voucher 132
    (5, 250, 25),   # Voucher 133
    (6, 200, 30),   # Voucher 134
    (2, 300, 5),    # Voucher 135
    (3, 350, 25),   # Voucher 136
    (4, 200, 20),   # Voucher 137
    (5, 250, 15),   # Voucher 138
    (6, 400, 10),   # Voucher 139
    (3, 450, 30),   # Voucher 140
    (4, 300, 25),   # Voucher 141
    (5, 200, 20),   # Voucher 142
    (6, 350, 15),   # Voucher 143
    (2, 400, 10),   # Voucher 144
    (3, 250, 15),   # Voucher 145
    (4, 200, 25),   # Voucher 146
    (5, 450, 20),   # Voucher 147
    (3, 300, 10),   # Voucher 149
    (7, 400, 15),   # Voucher 150
    (4, 350, 20),   # Voucher 151
    (5, 250, 25),   # Voucher 152
    (6, 200, 30),   # Voucher 153
    (2, 300, 5),    # Voucher 154
    (3, 350, 25),   # Voucher 155
    (4, 200, 20),   # Voucher 156
    (5, 250, 15),   # Voucher 157
    (6, 400, 10),   # Voucher 158
    (3, 450, 30),   # Voucher 159
    (4, 300, 25),   # Voucher 160
    (5, 200, 20),   # Voucher 161
    (6, 350, 15),   # Voucher 162
    (2, 400, 10),   # Voucher 163
    (3, 250, 15),   # Voucher 164
    (4, 200, 25),   # Voucher 165
    (5, 450, 20),   # Voucher 166
    (3, 300, 10),   # Voucher 168
    (7, 400, 15),   # Voucher 169
    (4, 350, 20),   # Voucher 170
    (5, 250, 25),   # Voucher 171
    (6, 200, 30),   # Voucher 172
    (2, 300, 5),    # Voucher 173
    (3, 350, 25),   # Voucher 174
    (4, 200, 20),   # Voucher 175
    (5, 250, 15),   # Voucher 176
    (6, 400, 10),   # Voucher 177
    (3, 450, 30),   # Voucher 178
    (4, 300, 25),   # Voucher 179
    (5, 200, 20),   # Voucher 180
    (6, 350, 15),   # Voucher 181
    (2, 400, 10),   # Voucher 182
    (3, 250, 15),   # Voucher 183
    (4, 200, 25),   # Voucher 184
    (5, 450, 20),   # Voucher 185
    (3, 300, 10),   # Voucher 187
    (7, 400, 15),   # Voucher 188
    (4, 350, 20),   # Voucher 189
    (5, 250, 25),   # Voucher 190
    (6, 200, 30),   # Voucher 191
    (2, 300, 5),    # Voucher 192
    (3, 350, 25),   # Voucher 193
    (4, 200, 20),   # Voucher 194
    (5, 250, 15),   # Voucher 195
    (6, 400, 10),   # Voucher 196
    (3, 450, 30),   # Voucher 197
    (4, 300, 25),   # Voucher 198
    (5, 200, 20),   # Voucher 199
    (6, 350, 15),   # Voucher 200
]





top_usable_vouchers = display_top_usable_vouchers(passengers, ticket_price)
print(f"Top 5 usable vouchers for {passengers} passengers and ticket price ${ticket_price}:")
for idx, (p, tp, d, _, savings) in enumerate(top_usable_vouchers, start=1):
    print(f"Voucher {idx}: Passengers: {p}, Ticket Price: ${tp}, Discount: {d}%, Savings: ${savings:.2f}")
