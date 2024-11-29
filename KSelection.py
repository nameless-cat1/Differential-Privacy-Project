import math
import time
import mysql.connector
import numpy as np


BETA = 1 / 10
EPSILON = 1
D = pow(10, 5)
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

def get_query_result():
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


    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='tpcd',
        auth_plugin='caching_sha2_password'
    )
    cursor = mydb.cursor()
    cursor.execute(query)
    result = np.array(cursor.fetchall())
    cursor.close()
    mydb.close()


    sorted_result = result[(-result[:, 1]).argsort()]
    u, t = np.hsplit(sorted_result, 2)
    return u.flatten(), t.flatten().astype(float)

def shift_inverse(f):
    s = np.full(D, -TAU - 1, dtype=int)
    for r in range(D):
        if f[TAU] == r:
            s[r] = 0
        else:
            j = binary_search(f, r)
            if 1 <= j <= TAU:
                s[r] = -TAU + j - 1
            elif TAU < j <= 2 * TAU:
                s[r] = TAU - j
    p = np.exp(EPSILON / 2 * s)
    p /= p.sum()
    r_tilde = np.random.choice(D, p=p)
    return r_tilde

def binary_search(f, r):
    low, high = 1, 2 * TAU
    while low <= high:
        mid = (low + high) // 2
        if f[mid] < r <= f[mid - 1]:
            return mid
        elif r <= f[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def k_selection(k, count, t, u):
    f = [0] * (2 * TAU + 1)
    j = 0
    for i in range(len(t)):
        if sum(sorted(count.values())[:-j or None]) <= k - 1:
            f[j] = t[i]
        else:
            j += 1
            if j > 2 * TAU:
                break
            else:
                f[j] = t[i]
        count[u[i]] += 1
    return f

def get_evaluation_error(t, r_tilde, percentile):
    r = np.percentile(t, percentile)
    relative_error = abs(r_tilde - r) / r
    print("The relative error: ", relative_error)
    return relative_error

user, tuple_counts = get_query_result()
print(user)
print(tuple_counts)

repeat_time = 5
relative_errors = []

count = {i: 0 for i in np.unique(user)}
f_k = k_selection(k=math.ceil(75 / 100 * len(tuple_counts)), count=count, t=tuple_counts, u=user)
print(f_k)

for i in range(repeat_time):
    r_tilde = shift_inverse(f_k)
    relative_errors.append(get_evaluation_error(t=tuple_counts, r_tilde=r_tilde, percentile=25))

print("The average relative error: ", np.average(relative_errors))
