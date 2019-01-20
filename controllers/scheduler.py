from ortools.sat.python import cp_model
import json

def negated_bounded_span(works, start, length):
    sequence = []
    # Left border (start of works, or works[start - 1])
    if start > 0:
        sequence.append(works[start - 1])
    for i in range(length):
        sequence.append(works[start + i].Not())
    # Right border (end of works or works[start + length])
    if start + length < len(works):
        sequence.append(works[start + length])
    return sequence


def add_soft_sequence_constraint(model, works, hard_min, soft_min, min_cost,
                                 soft_max, hard_max, max_cost, prefix):

    cost_literals = []
    cost_coefficients = []

    # Forbid sequences that are too short.
    for length in range(1, hard_min):
        for start in range(len(works) - length - 1):
            model.AddBoolOr(negated_bounded_span(works, start, length))

    # Penalize sequences that are below the soft limit.
    if min_cost > 0:
        for length in range(hard_min, soft_min):
            for start in range(len(works) - length - 1):
                span = negated_bounded_span(works, start, length)
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)
                span.append(lit)
                model.AddBoolOr(span)
                cost_literals.append(lit)
                # We filter exactly the sequence with a short length.
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

    # Penalize sequences that are above the soft limit.
    if max_cost > 0:
        for length in range(soft_max + 1, hard_max + 1):
            for start in range(len(works) - length - 1):
                span = negated_bounded_span(works, start, length)
                name = ': over_span(start=%i, length=%i)' % (start, length)
                lit = model.NewBoolVar(prefix + name)
                span.append(lit)
                model.AddBoolOr(span)
                cost_literals.append(lit)
                # Cost paid is max_cost * excess length.
                cost_coefficients.append(max_cost * (length - soft_max))

    # Just forbid any sequence of true variables with length hard_max + 1
    for start in range(len(works) - hard_max - 1):
        model.AddBoolOr(
            [works[i].Not() for i in range(start, start + hard_max + 1)])
    return cost_literals, cost_coefficients


def add_soft_sum_constraint(model, works, hard_min, soft_min, min_cost,
                            soft_max, hard_max, max_cost, prefix):
    
    cost_variables = []
    cost_coefficients = []
    sum_var = model.NewIntVar(hard_min, hard_max, '')
    # This adds the hard constraints on the sum.
    model.Add(sum_var == sum(works))

    # Penalize sums below the soft_min target.
    if soft_min > hard_min and min_cost > 0:
        delta = model.NewIntVar(-len(works), len(works), '')
        model.Add(delta == soft_min - sum_var)
        # TODO(user): Compare efficiency with only excess >= soft_min - sum_var.
        excess = model.NewIntVar(0, 7, prefix + ': under_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(min_cost)

    # Penalize sums above the soft_max target.
    if soft_max < hard_max and max_cost > 0:
        delta = model.NewIntVar(-7, 7, '')
        model.Add(delta == sum_var - soft_max)
        excess = model.NewIntVar(0, 7, prefix + ': over_sum')
        model.AddMaxEquality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(max_cost)

    return cost_variables, cost_coefficients


def solve_shift_scheduling(id_list,weeks):
    # Data
    employees = id_list   
    num_employees = len(employees) 
    num_weeks = weeks
    
    # shifts = ['O', 'M', 'A', 'N']
    shifts = ['0', '1', '2', '3']

    # Fixed assignment: (employee, shift, day).
    fixed_assignments = []

    # Request: (employee, shift, day, weight)
    # A negative weight indicates that the employee desire this assignment.
    # ex.
    # Employee 3 wants the first Saturday off, (3, 0, 5, -2)
    # Employee 5 wants a night shift on the second Thursday, (5, 3, 10, -2)
    # Employee 2 does not want a night shift on the third Friday, (2, 3, 4, 4)
    requests = []

    # Shift constraints on continuous sequence :
    #     (shift, hard_min, soft_min, min_penalty,
    #             soft_max, hard_max, max_penalty)
    shift_constraints = [
        # One or two consecutive days of rest, this is a hard constraint.
        (0, 1, 1, 0, 2, 2, 0),
        # betweem 2 and 3 consecutive days of night shifts, 1 and 4 are
        # possible but penalized.
        (3, 1, 2, 20, 3, 4, 5), #!
    ]

    # Weekly sum constraints on shifts days:
    #     (shift, hard_min, soft_min, min_penalty,
    #             soft_max, hard_max, max_penalty)
    weekly_sum_constraints = [
        # Constraints on rests per week.
        (0, 1, 1, 7, 2, 2, 4),
        # At least 1 night shift per week (penalized). At most 4 (hard).
        (3, 0, 1, 3, 4, 4, 0),
    ]
    # Penalized transitions:
    #     (previous_shift, next_shift, penalty (0 means forbidden))
    penalized_transitions = [

        # Afternoon to night has a penalty of 4.
        (2, 3, 4),

        # Night to morning is forbidden.
        (3, 1, 0),
    ] 

    # daily demands for work shifts (morning, afternon, night) for each day
    # of the week starting on Monday.
    weekly_cover_demands = [
        (1, 1, 1),  # Monday
        (1, 1, 1),  # Tuesday
        (1, 1, 1),  # Wednesday
        (1, 1, 1),  # Thursday
        (1, 1, 1),  # Friday
        (1, 1, 1),  # Saturday
        (1, 1, 1),  # Sunday
    ]

    # Penalty for exceeding the cover constraint per shift type.
    excess_cover_penalties = (2, 2, 5)

    num_days = num_weeks * 7
    num_shifts = len(shifts)

    model = cp_model.CpModel()

    work = {}
    for e in range(num_employees):
        for s in range(num_shifts):
            for d in range(num_days):
                work[e, s, d] = model.NewBoolVar('work%i_%i_%i' % (e, s, d))


    # Linear terms of the objective in a minimization context.
    obj_int_vars = []
    obj_int_coeffs = []
    obj_bool_vars = []
    obj_bool_coeffs = []

    # Exactly one shift per day.
    for e in range(num_employees):
        for d in range(num_days):
            model.Add(sum(work[e, s, d] for s in range(num_shifts)) == 1)

    # Fixed assignments.
    for e, s, d in fixed_assignments:
        model.Add(work[e, s, d] == 1)

    # Employee requests
    for e, s, d, w in requests:
        obj_bool_vars.append(work[e, s, d])
        obj_bool_coeffs.append(w)

    # Shift constraints
    for ct in shift_constraints:
        shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
        for e in range(num_employees):
            works = [work[e, shift, d] for d in range(num_days)]
            variables, coeffs = add_soft_sequence_constraint(
                model, works, hard_min, soft_min, min_cost, soft_max, hard_max,
                max_cost, 'shift_constraint(employee %i, shift %i)' % (e,
                                                                       shift))
            obj_bool_vars.extend(variables)
            obj_bool_coeffs.extend(coeffs)

    # Weekly sum constraints
    for ct in weekly_sum_constraints:
        shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
        for e in range(num_employees):
            for w in range(num_weeks):
                works = [work[e, shift, d + w * 7] for d in range(7)]
                variables, coeffs = add_soft_sum_constraint(
                    model, works, hard_min, soft_min, min_cost, soft_max,
                    hard_max, max_cost,
                    'weekly_sum_constraint(employee %i, shift %i, week %i)' %
                    (e, shift, w))
                obj_int_vars.extend(variables)
                obj_int_coeffs.extend(coeffs)

    # Penalized transitions
    for previous_shift, next_shift, cost in penalized_transitions:
        for e in range(num_employees):
            for d in range(num_days - 1):
                transition = [
                    work[e, previous_shift, d].Not(),
                    work[e, next_shift, d + 1].Not()
                ]
                if cost == 0:
                    model.AddBoolOr(transition)
                else:
                    trans_var = model.NewBoolVar(
                        'transition (employee=%i, day=%i)' % (e, d))
                    transition.append(trans_var)
                    model.AddBoolOr(transition)
                    obj_bool_vars.append(trans_var)
                    obj_bool_coeffs.append(cost)

    # Cover constraints
    for s in range(1, num_shifts):
        for w in range(num_weeks):
            for d in range(7):
                works = [work[e, s, w * 7 + d] for e in range(num_employees)]
                # Ignore Off shift.
                min_demand = weekly_cover_demands[d][s - 1]
                worked = model.NewIntVar(min_demand, num_employees, '')
                model.Add(worked == sum(works))
                over_penalty = excess_cover_penalties[s - 1]
                if over_penalty > 0:
                    name = 'excess_demand(shift=%i, week=%i, day=%i)' % (s, w,
                                                                         d)
                    excess = model.NewIntVar(0, num_employees - min_demand,
                                             name)
                    model.Add(excess == worked - min_demand)
                    obj_int_vars.append(excess)
                    obj_int_coeffs.append(over_penalty)

    # Objective
    model.Minimize(
        sum(obj_bool_vars[i] * obj_bool_coeffs[i]
            for i in range(len(obj_bool_vars)))
        + sum(obj_int_vars[i] * obj_int_coeffs[i]
              for i in range(len(obj_int_vars))))

    # Solve the model.
    solver = cp_model.CpSolver()
    solution_printer = cp_model.ObjectiveSolutionPrinter()
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    
    # Print solution.
    # if status == cp_model.OPTIMAL: 
    #     print('Status: %s' % ("OPTIMAL"))       
    #     str1 = ''
    #     for e in range(num_employees):
    #         str2 = ''
    #         for d in range(num_days):
    #             for s in range(num_shifts):
    #                 if solver.BooleanValue(work[e, s, d]):
    #                     str2 += '{"day":"%s", "shift":"%s"},' % (str(d),shifts[s])
    #         str2 = '[%s]' % str2[:-1]
    #         str1 += '{"employee":"%s","shifts":%s},' % (employees[e],str2)         
    #     json_str = '[%s]' % (str1[:-1])       
    #     # TODO: Add penalties to json.      
    #     return json_str

    if status == cp_model.OPTIMAL: 
        print('Status: %s' % ("OPTIMAL"))       
        str1 = ''
        for d in range(num_days):
            str2 = ''
            for s in range(num_shifts):
                for e in range(num_employees):
                    if solver.BooleanValue(work[e, s, d]):
                        str2 += '"%s",' % (employees[e])
            str2 = '[%s]' % (str2[:-1])
            str1 += '{"day":"%s","shifts":%s},' % (d, str2)
        json_str = '[%s]' % (str1[:-1]) 
        # TODO: Add penalties to json.      
        return json_str

    if status == cp_model.INFEASIBLE:
        return json.dumps({"message":"INFEASIBLE"})