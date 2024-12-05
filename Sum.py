import math
import mysql.connector
import numpy as np


BETA = 1 / 10
EPSILON = 1
D = pow(10, 7) * 2
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

def fetch_query_results():
    # Q18
    # query = (
    #     "select c_custkey, l_quantity "
    #     "from customer, orders, lineitem "
    #     "where c_custkey = o_custkey "
    #     "and l_orderkey = o_orderkey "
    #     "order by l_quantity"
    # )
    # Q9
    # query = (
    #     "select s_suppkey, (l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity)/1000 as num "
    #     "from supplier, partsupp, lineitem "
    #     "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey "
    #     "order by num"
    # )

    #Q7
    query = (
        "select 1,sum(l_extendedprice * (1 - l_discount)/1000) value "
        "from nation as n1, nation as n2, customer, supplier, orders, lineitem "
        "where n1.n_nationkey=c_nationkey and n2.n_nationkey=s_nationkey and c_custkey=o_custkey "
        "and s_suppkey=l_suppkey and o_orderkey=l_orderkey and l_shipdate>=date'1995-01-01' and l_shipdate<=date'1996-12-31' "
        "group by c_custkey, s_suppkey "
        "order by value"
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
    for r in range(D):
        if f[TAU] == r:
            shifts[r] = 0
        else:
            j = binary_search_algorithm(f, r)
            if 1 <= j <= TAU:
                shifts[r] = -TAU + j - 1
            elif TAU < j <= 2 * TAU:
                shifts[r] = TAU - j
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


def aggregate_counts(counts):
    sorted_counts = np.sort(counts)
    total_sum = np.sum(sorted_counts)
    f = [total_sum]
    for j in range(1, 2 * TAU + 1):
        f.append(total_sum - np.sum(sorted_counts[-j:]))
    return f


def calculate_relative_error(actual, estimated):
    actual_sum = np.sum(actual)
    relative_error = abs(estimated - actual_sum) / actual_sum
    print("The relative error: ", relative_error)
    return relative_error


item_values = fetch_query_results()
print(item_values)


repetitions = 5
errors = []
f_k = aggregate_counts(item_values)
print(np.sum(item_values))

for _ in range(repetitions):
    estimated_value = compute_shift_inverse(f_k)
    errors.append(calculate_relative_error(item_values, estimated_value))

print("The average relative error: ", np.average(errors))