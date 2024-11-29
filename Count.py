import math
import mysql.connector
import numpy as np

BETA = 1 / 10
EPSILON = 1
D = pow(10, 6)
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

def fetch_data_from_db():
    # Q18
    #
    # query = (
    #     "select c_custkey, count(*) as count "
    #     "from customer, orders, lineitem "
    #     "where c_custkey = o_custkey "
    #     "and l_orderkey = o_orderkey "
    #     "group by c_custkey "
    #     "order by count "
    # )

    # Q12
    query = (
        "select o_orderkey, count(*) as count "
        "from orders, lineitem "
        "where o_orderkey = l_orderkey "
        "group by o_orderkey "
        "order by count"
    )

    # Q9
    # query = (
    #     "select s_suppkey, count(*) as count "
    #     "from supplier, partsupp, lineitem "
    #     "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey "
    #     "group by s_suppkey "
    #     "order by count"
    # )

    # Q5
    # query = (
    #     "select n_nationkey, count(*) as count "
    #     "from customer,orders,lineitem,supplier,nation,region "
    #     "where c_custkey = o_custkey and l_orderkey = o_orderkey "
    #     "and l_suppkey = s_suppkey "
    #     "and c_nationkey = s_nationkey "
    #     "and s_nationkey = n_nationkey "
    #     "and n_regionkey = r_regionkey "
    #     "group by n_nationkey "
    #     "order by count"
    # )

    # Q9
    # query = (
    #     "select 1, s_suppkey "
    #     "from supplier, partsupp, lineitem "
    #     "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey"
    # )

    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tpcd',
        auth_plugin='caching_sha2_password'
    )
    cursor = connection.cursor()
    cursor.execute(query)
    results = np.array(cursor.fetchall())
    cursor.close()
    connection.close()


    sorted_results = results[results[:, 1].argsort()[::-1]]
    keys, counts = np.hsplit(sorted_results, 2)
    return keys.flatten(), counts.flatten().astype(float)


def compute_shift_inverse(f):
    shifts = np.full(D, -TAU - 1, dtype=int)
    for i in range(D):
        if f[TAU] == i:
            shifts[i] = 0
        else:
            pos = binary_search(f, i)
            if 1 <= pos <= TAU:
                shifts[i] = -TAU + pos - 1
            elif TAU < pos <= 2 * TAU:
                shifts[i] = TAU - pos
    probabilities = np.exp(EPSILON / 2 * shifts)
    probabilities /= probabilities.sum()
    estimated_index = np.random.choice(D, p=probabilities)
    return estimated_index


def binary_search(f, target):
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


def aggregate_values(counts):
    sorted_counts = np.sort(counts)
    total_sum = np.sum(sorted_counts)
    aggregated_f = [total_sum]
    for j in range(1, 2 * TAU + 1):
        aggregated_f.append(total_sum - np.sum(sorted_counts[-j:]))
    return aggregated_f


def calculate_relative_error(actual, estimated):
    actual_total = np.sum(actual)
    relative_error = abs(estimated - actual_total) / actual_total
    print("The relative error: ", relative_error)
    return relative_error



user_keys, item_counts = fetch_data_from_db()
print(user_keys)
print(item_counts)


repetitions = 5
errors = []
f_k = aggregate_values(item_counts)
print(np.sum(item_counts))

for _ in range(repetitions):
    estimated_value = compute_shift_inverse(f_k)
    errors.append(calculate_relative_error(item_counts, estimated_value))

print("The average relative error: ", np.average(errors))