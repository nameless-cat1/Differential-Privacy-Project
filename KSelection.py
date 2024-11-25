import math
import time

import mysql.connector
import numpy as np


def get_query_result():


    # Q18
    query = (
        "select c_custkey, l_quantity "
        "from customer, orders, lineitem "
        "where c_custkey = o_custkey "
        "and l_orderkey = o_orderkey "
    )

    # Q9
    # query = (
    #     "select s_suppkey, (l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity)/1000 as num "
    #     "from supplier, partsupp, lineitem "
    #     "where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey "
    #     "order by num"
    # )

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
    sorted_result = result[(-result[:, 1]).argsort()]
    u, t = np.hsplit(sorted_result, 2)
    u = u.flatten()
    t = t.flatten().astype(float)
    return u, t



def shift_inverse(f):
    s = [-TAU - 1] * D
    for r in range(D):
        if r == f[TAU]:
            s[r] = 0
        else:
            j = binary_search(f, r)
            if j != -1:
                if TAU < j <= 2 * TAU:
                    s[r] = TAU - j
                elif 1 <= j <= TAU:
                    s[r] = -TAU + j - 1
    p = np.array([np.exp(EPSILON / 2 * s[r]) for r in range(D)])
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
                return f
            else:
                f[j] = t[i]
        count[u[i]] += 1
    return f


def get_evaluation_error(t, r_tilde, percentile):
    r = np.percentile(t, percentile)
    relative_error = abs(r_tilde - r) / r
    print("The relative_error: ", relative_error)
    return relative_error
    # rank_error = 0
    # if relative_error != 0 and r_tilde in t:
    #     r_tilde_index = np.where(t == r_tilde)
    #     rank_error = r_tilde_index[0][0] - math.ceil((100 - percentile) / 100 * len(t))
    # print("The rank error: ", rank_error)

start_time = time.time()
BETA = 1 / 10
EPSILON = 1
D = pow(10, 5)
TAU = math.ceil(2 / EPSILON * math.log((D + 1) / BETA))

user, tuple = get_query_result()

print(user)
print(tuple)

repeat_time=5
relative_errors=[]

count = {i: 0 for i in np.unique(user)}
# f_k = k_selection(k=0, count=count,t=tuple,u=user)
f_k = k_selection(k=math.ceil(25 / 100 * len(tuple)), count=count, t=tuple, u=user)
print(f_k)

for i in range(repeat_time):
    r_tilde = shift_inverse(f_k)
    relative_errors.append(get_evaluation_error(t=tuple, r_tilde=r_tilde, percentile=75))

print("The average relative_error: ", np.average(relative_errors))

end_time = time.time()

elapsed_time = end_time - start_time
print(f"running time: {elapsed_time:.6f} s")