import math
import time
import mysql.connector
import numpy as np


BETA = 1 / 10
EPSILON = 1
D = pow(10, 5)
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

def fetch_query_results():
    # Q18
    # query = (
    #     "select c_custkey, l_quantity "
    #     "from customer, orders, lineitem "
    #     "where c_custkey = o_custkey "
    #     "and l_orderkey = o_orderkey "
    # )

    # Q9
    query = (
        "select s_suppkey, (l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity)/1000 as num "
        "from supplier, partsupp, lineitem "
        "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey "
        "order by num"
    )

    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tpcd',
        auth_plugin='caching_sha2_password'
    )
    cursor = db_connection.cursor()
    cursor.execute(query)
    results = np.array(cursor.fetchall())
    cursor.close()
    db_connection.close()


    sorted_results = results[(-results[:, 1]).argsort()]
    _, values = np.hsplit(sorted_results, 2)
    return values.flatten().astype(float)


def compute_shift_inverse(f):
    shifts = np.full(D, -TAU - 1, dtype=int)
    for i in range(D):
        if f[TAU] == i:
            shifts[i] = 0
        else:
            pos = binary_search_algorithm(f, i)
            if 1 <= pos <= TAU:
                shifts[i] = -TAU + pos - 1
            elif TAU < pos <= 2 * TAU:
                shifts[i] = TAU - pos
    probabilities = np.exp(EPSILON / 2 * shifts)
    probabilities /= probabilities.sum()
    estimated_index = np.random.choice(D, p=probabilities)
    return estimated_index


def binary_search_algorithm(f, target):
    low, high = 1, 2 * TAU
    while low <= high:
        mid = (low + high) // 2
        if f[mid] < target <= f[mid - 1]:
            return mid
        elif target <= f[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def select_k_values(k, counts, t, u):
    f = [0] * (2 * TAU + 1)
    j = 0
    for i in range(len(t)):
        if sum(sorted(counts.values())[:-j or None]) <= k - 1:
            f[j] = t[i]
        else:
            j += 1
            if j > 2 * TAU:
                break
            else:
                f[j] = t[i]
        counts[u[i]] += 1
    return f


def calculate_relative_error(actual, estimated, percentile):
    actual_value = np.percentile(actual, percentile)
    relative_error = abs(estimated - actual_value) / actual_value
    print("The relative error: ", relative_error)
    return relative_error



user_keys, item_values = fetch_query_results()
print(user_keys)
print(item_values)


repetitions = 5
errors = []
count_dict = {i: 0 for i in np.unique(user_keys)}
f_k = select_k_values(k=math.ceil(75 / 100 * len(item_values)), counts=count_dict, t=item_values,
                                  u=user_keys)
print(f_k)

for _ in range(repetitions):
    estimated_value = compute_shift_inverse(f_k)
    errors.append(calculate_relative_error(actual=item_values, estimated=estimated_value, percentile=25))

print("The average relative error: ", np.average(errors))