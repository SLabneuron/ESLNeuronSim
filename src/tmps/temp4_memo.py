for idx in range(total_iterations):

    Q = Q_list[idx]
    S = S_list[idx]
    x_max = x_max_list[idx]
    x_min = x_min_list[idx]

    result = self.analyze_results(Q, S, x_max, x_min)
    result_list.append(result)