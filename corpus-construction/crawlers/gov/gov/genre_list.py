import pickle

sort_by_search_term = True

genre_list = [('annual report',),
              ('call for evidence',),
              ('economic estimates',),
              ('evaluation',),
              ('evidence assessment',),
              ('export of objects',),
              ('freedom of information', 'FoI', 'foi'),
              ('funding agreement',),
              ('green paper',),
              ('equality impact assessment',),
              ('regulatory impact assessment',),
              ('impact assessment',),
              ('consultation',),
              ('market impact',),
              ('letter',),
              ('role specification',),
              ('spending review',),
              ('strategy',),
              ('survey',),
              ('tailored review',),
              ('technical report',),
              ('white paper',),
              ('minutes',)]

if sort_by_search_term:

    genre_list = [tuple[0] for tuple in genre_list]

pickle.dump(genre_list, open('genre_list', 'wb'))
