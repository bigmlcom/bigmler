# -*- coding: utf-8 -*-
def predict_rating(gender=None,
                   age_range=None,
                   occupation=None,
                   zipcode=None,
                   title=None,
                   genres=None,
                   timestamp=None):
    """ Predictor for rating

        Created using BigMLer
    """

    import re

    tm_tokens = 'tokens_only'
    tm_full_term = 'full_terms_only'
    tm_all = 'all'

    def term_matches(text, field_name, term):
        """ Counts the number of occurences of term and its variants in text

        """
        forms_list = term_forms[field_name].get(term, [term])
        options = term_analysis[field_name]
        token_mode = options.get('token_mode', tm_tokens)
        case_sensitive = options.get('case_sensitive', False)
        first_term = forms_list[0]
        if token_mode == tm_full_term:
            return full_term_match(text, first_term, case_sensitive)
        else:
            # In token_mode='all' we will match full terms using equals and
            # tokens using contains
            if token_mode == tm_all and len(forms_list) == 1:
                pattern = re.compile(r'^.+\b.+$', re.U)
                if re.match(pattern, first_term):
                    return full_term_match(text, first_term, case_sensitive)
            return term_matches_tokens(text, forms_list, case_sensitive)


    def full_term_match(text, full_term, case_sensitive):
        """Counts the match for full terms according to the case_sensitive
              option

        """
        if not case_sensitive:
            text = text.lower()
            full_term = full_term.lower()
        return 1 if text == full_term else 0

    def get_tokens_flags(case_sensitive):
        """Returns flags for regular expression matching depending on text
              analysis options

        """
        flags = re.U
        if not case_sensitive:
            flags = (re.I | flags)
        return flags


    def term_matches_tokens(text, forms_list, case_sensitive):
        """ Counts the number of occurrences of the words in forms_list in
               the text

        """
        flags = get_tokens_flags(case_sensitive)
        expression = r'(\b|_)%s(\b|_)' % '(\\b|_)|(\\b|_)'.join(forms_list)
        pattern = re.compile(expression, flags=flags)
        matches = re.findall(pattern, text)
        return len(matches)

    term_analysis = {
        "title": {
            "case_sensitive": False,
            "token_mode": 'all',
        },
    }
    term_forms = {
        "title": {
            "beauty": ['beauty', 'beautiful'],
            "day": ['day', 'days'],
        },
    }

    def item_matches(text, field_name, item):
        """ Counts the number of occurrences of item in text

        """
        options = item_analysis[field_name]
        separator = options.get('separator', ' ')
        regexp = options.get('separator_regexp')
        if regexp is None:
            regexp = r"%s" % re.escape(separator)
        return count_items_matches(text, item, regexp)


    def count_items_matches(text, item, regexp):
        """ Counts the number of occurrences of the item in the text

        """
        expression = r'(^|%s)%s($|%s)' % (regexp, item, regexp)
        pattern = re.compile(expression, flags=re.U)
        matches = re.findall(pattern, text)
        return len(matches)

    item_analysis = {
        "genres": {
            "separator": '$',
        },
    }

    if (genres is None):
        return {"prediction": 3.7, "error": 1.28278}
    if (item_matches(genres, "genres", u"Comedy") > 0):
        if (title is None):
            return {"prediction": 3.39535, "error": 1.57231}
        if (term_matches(title, "title", u"life") > 0):
            return {"prediction":5, "error":0.90777}
        if (term_matches(title, "title", u"life") <= 0):
            if (term_matches(title, "title", u"forrest gump (1994)") > 0):
                return {"prediction":5, "error":1.09624}
            if (term_matches(title, "title", u"forrest gump (1994)") <= 0):
                if (term_matches(title, "title", u"1983") > 0):
                    return {"prediction":5, "error":1.08292}
                if (term_matches(title, "title", u"1983") <= 0):
                    if (zipcode is None):
                        return {"prediction": 3.25316, "error": 1.5086}
                    if (zipcode > 7753):
                        if (item_matches(genres, "genres", u"Horror") > 0):
                            if (timestamp is None):
                                return {"prediction": 2, "error": 5.08228}
                            if (timestamp > 978258115):
                                return {"prediction":1.5, "error":5.26764}
                            if (timestamp <= 978258115):
                                return {"prediction":3, "error":5.08228}
                        if (item_matches(genres, "genres", u"Horror") <= 0):
                            if (timestamp is None):
                                return {"prediction": 3.3913, "error": 1.43342}
                            if (timestamp > 978218758):
                                if (item_matches(genres, "genres", u"Thriller") > 0):
                                    return {"prediction":2, "error":10.53528}
                                if (item_matches(genres, "genres", u"Thriller") <= 0):
                                    if (item_matches(genres, "genres", u"Crime") > 0):
                                        return {"prediction":5, "error":0.9578}
                                    if (item_matches(genres, "genres", u"Crime") <= 0):
                                        if (term_matches(title, "title", u"breakfast club, the (1985)") > 0):
                                            return {"prediction":2, "error":1.31722}
                                        if (term_matches(title, "title", u"breakfast club, the (1985)") <= 0):
                                            if (term_matches(title, "title", u"monty") > 0):
                                                return {"prediction":2, "error":1.28344}
                                            if (term_matches(title, "title", u"monty") <= 0):
                                                if (term_matches(title, "title", u"stand by me (1986)") > 0):
                                                    return {"prediction":5, "error":1.24322}
                                                if (term_matches(title, "title", u"stand by me (1986)") <= 0):
                                                    if (timestamp > 978228710):
                                                        if (item_matches(genres, "genres", u"Musical") > 0):
                                                            return {"prediction":4.5, "error":5.26764}
                                                        if (item_matches(genres, "genres", u"Musical") <= 0):
                                                            if (item_matches(genres, "genres", u"Romance") > 0):
                                                                if (term_matches(title, "title", u"day") > 0):
                                                                    return {"prediction":2, "error":1.38964}
                                                                if (term_matches(title, "title", u"day") <= 0):
                                                                    if (timestamp > 978428301):
                                                                        return {"prediction":4, "error":1.13085}
                                                                    if (timestamp <= 978428301):
                                                                        if (term_matches(title, "title", u"shakespeare in love (1998)") > 0):
                                                                            return {"prediction":4, "error":0.958}
                                                                        if (term_matches(title, "title", u"shakespeare in love (1998)") <= 0):
                                                                            return {"prediction":3, "error":0.36209}
                                                            if (item_matches(genres, "genres", u"Romance") <= 0):
                                                                if (occupation is None):
                                                                    return {"prediction": 3.65385, "error": 1.31541}
                                                                if (occupation == "writer"):
                                                                    return {"prediction":5, "error":1.31541}
                                                                if (occupation != "writer"):
                                                                    if (item_matches(genres, "genres", u"Drama") > 0):
                                                                        if (term_matches(title, "title", u"1997") > 0):
                                                                            return {"prediction":5, "error":1.56826}
                                                                        if (term_matches(title, "title", u"1997") <= 0):
                                                                            return {"prediction":4, "error":0.78413}
                                                                    if (item_matches(genres, "genres", u"Drama") <= 0):
                                                                        if (timestamp > 978298248):
                                                                            if (timestamp > 978298391):
                                                                                if (gender is None):
                                                                                    return {"prediction": 3.6, "error": 1.92072}
                                                                                if (gender == "Female"):
                                                                                    return {"prediction":4, "error":1.35815}
                                                                                if (gender == "Male"):
                                                                                    if (term_matches(title, "title", u"1996") > 0):
                                                                                        return {"prediction":4, "error":2.93426}
                                                                                    if (term_matches(title, "title", u"1996") <= 0):
                                                                                        return {"prediction":3, "error":2.07483}
                                                                            if (timestamp <= 978298391):
                                                                                return {"prediction":5, "error":2.36951}
                                                                        if (timestamp <= 978298248):
                                                                            if (term_matches(title, "title", u"1980") > 0):
                                                                                return {"prediction":2, "error":1.31017}
                                                                            if (term_matches(title, "title", u"1980") <= 0):
                                                                                if (timestamp > 978297750):
                                                                                    if (term_matches(title, "title", u"1999") > 0):
                                                                                        return {"prediction":3, "error":1.14938}
                                                                                    if (term_matches(title, "title", u"1999") <= 0):
                                                                                        return {"prediction":4, "error":0.81274}
                                                                                if (timestamp <= 978297750):
                                                                                    if (term_matches(title, "title", u"1994") > 0):
                                                                                        return {"prediction":4, "error":1.09476}
                                                                                    if (term_matches(title, "title", u"1994") <= 0):
                                                                                        return {"prediction":3, "error":0.44694}
                                                    if (timestamp <= 978228710):
                                                        if (timestamp > 978226820):
                                                            return {"prediction":5, "error":2.93426}
                                                        if (timestamp <= 978226820):
                                                            return {"prediction":4, "error":2.07483}
                            if (timestamp <= 978218758):
                                if (term_matches(title, "title", u"1994") > 0):
                                    return {"prediction":1, "error":1.96692}
                                if (term_matches(title, "title", u"1994") <= 0):
                                    if (timestamp > 978174603):
                                        if (term_matches(title, "title", u"1999") > 0):
                                            if (timestamp > 978200667):
                                                return {"prediction":1, "error":3.89486}
                                            if (timestamp <= 978200667):
                                                if (timestamp > 978196617):
                                                    return {"prediction":3, "error":2.07483}
                                                if (timestamp <= 978196617):
                                                    return {"prediction":2, "error":2.93426}
                                        if (term_matches(title, "title", u"1999") <= 0):
                                            if (occupation is None):
                                                return {"prediction": 3.09091, "error": 1.95519}
                                            if (occupation == "executive/managerial"):
                                                return {"prediction":4, "error":1.38253}
                                            if (occupation != "executive/managerial"):
                                                if (timestamp > 978200651):
                                                    if (term_matches(title, "title", u"bride") > 0):
                                                        return {"prediction":2, "error":2.36951}
                                                    if (term_matches(title, "title", u"bride") <= 0):
                                                        if (timestamp > 978202404):
                                                            return {"prediction":3, "error":1.35815}
                                                        if (timestamp <= 978202404):
                                                            if (term_matches(title, "title", u"batman") > 0):
                                                                return {"prediction":3, "error":2.93426}
                                                            if (term_matches(title, "title", u"batman") <= 0):
                                                                return {"prediction":4, "error":2.07483}
                                                if (timestamp <= 978200651):
                                                    if (item_matches(genres, "genres", u"Romance") > 0):
                                                        return {"prediction":3, "error":2.93426}
                                                    if (item_matches(genres, "genres", u"Romance") <= 0):
                                                        return {"prediction":2, "error":2.07483}
                                    if (timestamp <= 978174603):
                                        if (term_matches(title, "title", u"1985") > 0):
                                            return {"prediction":5, "error":2.93395}
                                        if (term_matches(title, "title", u"1985") <= 0):
                                            if (occupation is None):
                                                return {"prediction": 3.5, "error": 2.34869}
                                            if (occupation == "sales/marketing"):
                                                return {"prediction":4, "error":2.34869}
                                            if (occupation != "sales/marketing"):
                                                if (timestamp > 978174551):
                                                    return {"prediction":4, "error":2.93426}
                                                if (timestamp <= 978174551):
                                                    return {"prediction":3, "error":2.07483}
                    if (zipcode <= 7753):
                        if (item_matches(genres, "genres", u"Drama") > 0):
                            return {"prediction":4, "error":2.60606}
                        if (item_matches(genres, "genres", u"Drama") <= 0):
                            if (timestamp is None):
                                return {"prediction": 1.8, "error": 2.93395}
                            if (timestamp > 978904214):
                                if (term_matches(title, "title", u"1997") > 0):
                                    return {"prediction":3, "error":2.93426}
                                if (term_matches(title, "title", u"1997") <= 0):
                                    return {"prediction":2, "error":2.07483}
                            if (timestamp <= 978904214):
                                return {"prediction":1, "error":2.07461}
    if (item_matches(genres, "genres", u"Comedy") <= 0):
        if (title is None):
            return {"prediction": 3.82843, "error": 1.25974}
        if (term_matches(title, "title", u"1995") > 0):
            if (occupation is None):
                return {"prediction": 2.66667, "error": 3.25095}
            if (occupation == "clerical/admin"):
                return {"prediction":1, "error":3.25095}
            if (occupation != "clerical/admin"):
                if (item_matches(genres, "genres", u"Romance") > 0):
                    return {"prediction":4, "error":2.47964}
                if (item_matches(genres, "genres", u"Romance") <= 0):
                    if (occupation == "writer"):
                        return {"prediction":2, "error":2.03402}
                    if (occupation != "writer"):
                        return {"prediction":3, "error":1.17434}
        if (term_matches(title, "title", u"1995") <= 0):
            if (item_matches(genres, "genres", u"Horror") > 0):
                if (timestamp is None):
                    return {"prediction": 3.35, "error": 2.2498}
                if (timestamp > 978200824):
                    if (timestamp > 978876267):
                        return {"prediction":2, "error":1.97983}
                    if (timestamp <= 978876267):
                        if (item_matches(genres, "genres", u"Thriller") > 0):
                            if (term_matches(title, "title", u"alien") > 0):
                                return {"prediction":4, "error":2.93426}
                            if (term_matches(title, "title", u"alien") <= 0):
                                return {"prediction":3, "error":2.07483}
                        if (item_matches(genres, "genres", u"Thriller") <= 0):
                            if (timestamp > 978268588):
                                if (term_matches(title, "title", u"king") > 0):
                                    return {"prediction":4, "error":2.03402}
                                if (term_matches(title, "title", u"king") <= 0):
                                    return {"prediction":5, "error":1.17434}
                            if (timestamp <= 978268588):
                                if (term_matches(title, "title", u"alien") > 0):
                                    return {"prediction":3, "error":1.56826}
                                if (term_matches(title, "title", u"alien") <= 0):
                                    return {"prediction":4, "error":0.78413}
                if (timestamp <= 978200824):
                    if (occupation is None):
                        return {"prediction": 2.42857, "error": 3.28429}
                    if (occupation == "academic/educator"):
                        if (term_matches(title, "title", u"1960") > 0):
                            return {"prediction":4, "error":2.93426}
                        if (term_matches(title, "title", u"1960") <= 0):
                            return {"prediction":3, "error":2.07483}
                    if (occupation != "academic/educator"):
                        if (term_matches(title, "title", u"bringing") > 0):
                            return {"prediction":3, "error":3.89486}
                        if (term_matches(title, "title", u"bringing") <= 0):
                            if (timestamp > 978200492):
                                return {"prediction":2, "error":2.93426}
                            if (timestamp <= 978200492):
                                return {"prediction":1, "error":2.07483}
            if (item_matches(genres, "genres", u"Horror") <= 0):
                if (gender is None):
                    return {"prediction": 3.92135, "error": 1.21004}
                if (gender == "Male"):
                    if (term_matches(title, "title", u"dick tracy (1990)") > 0):
                        return {"prediction":1, "error":1.29316}
                    if (term_matches(title, "title", u"dick tracy (1990)") <= 0):
                        if (occupation is None):
                            return {"prediction": 3.84892, "error": 1.26101}
                        if (occupation == "writer"):
                            if (timestamp is None):
                                return {"prediction": 3.2, "error": 2.52836}
                            if (timestamp > 978243869):
                                if (item_matches(genres, "genres", u"Romance") > 0):
                                    return {"prediction":4, "error":2.5701}
                                if (item_matches(genres, "genres", u"Romance") <= 0):
                                    if (timestamp > 978246320):
                                        if (timestamp > 978246556):
                                            return {"prediction":2, "error":2.93426}
                                        if (timestamp <= 978246556):
                                            return {"prediction":3, "error":2.07483}
                                    if (timestamp <= 978246320):
                                        return {"prediction":2, "error":1.35815}
                            if (timestamp <= 978243869):
                                if (term_matches(title, "title", u"1994") > 0):
                                    return {"prediction":3, "error":3.32155}
                                if (term_matches(title, "title", u"1994") <= 0):
                                    if (item_matches(genres, "genres", u"Film-Noir") > 0):
                                        return {"prediction":4, "error":2.93426}
                                    if (item_matches(genres, "genres", u"Film-Noir") <= 0):
                                        return {"prediction":4.5, "error":5.26764}
                        if (occupation != "writer"):
                            if (term_matches(title, "title", u"2000") > 0):
                                if (term_matches(title, "title", u"mission") > 0):
                                    return {"prediction":2.5, "error":5.26764}
                                if (term_matches(title, "title", u"mission") <= 0):
                                    if (term_matches(title, "title", u"cell") > 0):
                                        return {"prediction":3, "error":1.09476}
                                    if (term_matches(title, "title", u"cell") <= 0):
                                        if (timestamp is None):
                                            return {"prediction": 3.6, "error": 1.92072}
                                        if (timestamp > 978217782):
                                            return {"prediction":3, "error":1.35815}
                                        if (timestamp <= 978217782):
                                            return {"prediction":4, "error":1.10893}
                            if (term_matches(title, "title", u"2000") <= 0):
                                if (timestamp is None):
                                    return {"prediction": 3.95, "error": 1.26219}
                                if (timestamp > 978298955):
                                    if (timestamp > 1009669148):
                                        if (term_matches(title, "title", u"1997") > 0):
                                            return {"prediction":5, "error":2.93426}
                                        if (term_matches(title, "title", u"1997") <= 0):
                                            return {"prediction":4, "error":2.07483}
                                    if (timestamp <= 1009669148):
                                        if (term_matches(title, "title", u"1989") > 0):
                                            return {"prediction":5, "error":1.59717}
                                        if (term_matches(title, "title", u"1989") <= 0):
                                            if (term_matches(title, "title", u"1990") > 0):
                                                return {"prediction":2, "error":1.16977}
                                            if (term_matches(title, "title", u"1990") <= 0):
                                                if (item_matches(genres, "genres", u"Film-Noir") > 0):
                                                    return {"prediction":4, "error":0.95152}
                                                if (item_matches(genres, "genres", u"Film-Noir") <= 0):
                                                    if (term_matches(title, "title", u"1980") > 0):
                                                        return {"prediction":4, "error":0.77415}
                                                    if (term_matches(title, "title", u"1980") <= 0):
                                                        return {"prediction":3, "error":0.25805}
                                if (timestamp <= 978298955):
                                    if (term_matches(title, "title", u"1987") > 0):
                                        return {"prediction":1, "error":1.28682}
                                    if (term_matches(title, "title", u"1987") <= 0):
                                        if (term_matches(title, "title", u"fight") > 0):
                                            return {"prediction":2, "error":1.23008}
                                        if (term_matches(title, "title", u"fight") <= 0):
                                            if (term_matches(title, "title", u"1993") > 0):
                                                if (timestamp > 978234034):
                                                    return {"prediction":4, "error":0.89387}
                                                if (timestamp <= 978234034):
                                                    return {"prediction":3, "error":0.77411}
                                            if (term_matches(title, "title", u"1993") <= 0):
                                                if (term_matches(title, "title", u"1996") > 0):
                                                    if (occupation == "other"):
                                                        return {"prediction":1, "error":2.43201}
                                                    if (occupation != "other"):
                                                        if (item_matches(genres, "genres", u"Drama") > 0):
                                                            return {"prediction":5, "error":1.38965}
                                                        if (item_matches(genres, "genres", u"Drama") <= 0):
                                                            if (zipcode is None):
                                                                return {"prediction": 3.75, "error": 1.96736}
                                                            if (zipcode > 94327):
                                                                return {"prediction":5, "error":1.96736}
                                                            if (zipcode <= 94327):
                                                                if (item_matches(genres, "genres", u"Thriller") > 0):
                                                                    return {"prediction":5, "error":1.90304}
                                                                if (item_matches(genres, "genres", u"Thriller") <= 0):
                                                                    if (occupation == "executive/managerial"):
                                                                        return {"prediction":3, "error":10.53528}
                                                                    if (occupation != "executive/managerial"):
                                                                        if (zipcode > 58365):
                                                                            return {"prediction":3, "error":0.99163}
                                                                        if (zipcode <= 58365):
                                                                            if (timestamp > 978297836):
                                                                                return {"prediction":3, "error":1.28505}
                                                                            if (timestamp <= 978297836):
                                                                                return {"prediction":4, "error":0.57469}
                                                if (term_matches(title, "title", u"1996") <= 0):
                                                    if (term_matches(title, "title", u"negotiator") > 0):
                                                        return {"prediction":3, "error":0.82118}
                                                    if (term_matches(title, "title", u"negotiator") <= 0):
                                                        if (item_matches(genres, "genres", u"War") > 0):
                                                            if (timestamp > 978201771):
                                                                if (timestamp > 978294214):
                                                                    if (timestamp > 978295884):
                                                                        return {"prediction":4, "error":2.07483}
                                                                    if (timestamp <= 978295884):
                                                                        return {"prediction":5, "error":2.93426}
                                                                if (timestamp <= 978294214):
                                                                    if (timestamp > 978211160):
                                                                        if (timestamp > 978294061):
                                                                            return {"prediction":2, "error":2.03402}
                                                                        if (timestamp <= 978294061):
                                                                            return {"prediction":3, "error":1.17434}
                                                                    if (timestamp <= 978211160):
                                                                        return {"prediction":4, "error":2.47964}
                                                            if (timestamp <= 978201771):
                                                                return {"prediction":5, "error":2.56453}
                                                        if (item_matches(genres, "genres", u"War") <= 0):
                                                            if (occupation == "K-12 student"):
                                                                if (timestamp > 978146981):
                                                                    return {"prediction":4, "error":2.93426}
                                                                if (timestamp <= 978146981):
                                                                    return {"prediction":3, "error":2.07483}
                                                            if (occupation != "K-12 student"):
                                                                if (timestamp > 978201899):
                                                                    if (timestamp > 978215603):
                                                                        if (item_matches(genres, "genres", u"Adventure") > 0):
                                                                            if (zipcode is None):
                                                                                return {"prediction": 4.72727, "error": 1.09872}
                                                                            if (zipcode > 22103):
                                                                                if (term_matches(title, "title", u"1994") > 0):
                                                                                    return {"prediction":4, "error":1.72408}
                                                                                if (term_matches(title, "title", u"1994") <= 0):
                                                                                    if (term_matches(title, "title", u"king") > 0):
                                                                                        return {"prediction":4, "error":1.92072}
                                                                                    if (term_matches(title, "title", u"king") <= 0):
                                                                                        if (term_matches(title, "title", u"jones") > 0):
                                                                                            return {"prediction":4, "error":2.03402}
                                                                                        if (term_matches(title, "title", u"jones") <= 0):
                                                                                            return {"prediction":5, "error":1.17434}
                                                                            if (zipcode <= 22103):
                                                                                return {"prediction":5, "error":0.49136}
                                                                        if (item_matches(genres, "genres", u"Adventure") <= 0):
                                                                            if (timestamp > 978294097):
                                                                                if (term_matches(title, "title", u"1960") > 0):
                                                                                    return {"prediction":3, "error":1.25106}
                                                                                if (term_matches(title, "title", u"1960") <= 0):
                                                                                    if (timestamp > 978294245):
                                                                                        if (timestamp > 978298584):
                                                                                            return {"prediction":5, "error":0.80826}
                                                                                        if (timestamp <= 978298584):
                                                                                            if (term_matches(title, "title", u"terminator") > 0):
                                                                                                return {"prediction":5, "error":1.18675}
                                                                                            if (term_matches(title, "title", u"terminator") <= 0):
                                                                                                if (term_matches(title, "title", u"1994") > 0):
                                                                                                    return {"prediction":5, "error":1.18253}
                                                                                                if (term_matches(title, "title", u"1994") <= 0):
                                                                                                    if (occupation == "scientist"):
                                                                                                        return {"prediction":5, "error":1.13085}
                                                                                                    if (occupation != "scientist"):
                                                                                                        if (term_matches(title, "title", u"1976") > 0):
                                                                                                            return {"prediction":5, "error":0.958}
                                                                                                        if (term_matches(title, "title", u"1976") <= 0):
                                                                                                            return {"prediction":4, "error":0.36209}
                                                                                    if (timestamp <= 978294245):
                                                                                        return {"prediction":5, "error":0.60498}
                                                                            if (timestamp <= 978294097):
                                                                                if (timestamp > 978230086):
                                                                                    if (timestamp > 978234842):
                                                                                        return {"prediction":4, "error":1.09476}
                                                                                    if (timestamp <= 978234842):
                                                                                        if (term_matches(title, "title", u"truman") > 0):
                                                                                            return {"prediction":4, "error":1.56826}
                                                                                        if (term_matches(title, "title", u"truman") <= 0):
                                                                                            return {"prediction":3, "error":0.78413}
                                                                                if (timestamp <= 978230086):
                                                                                    if (term_matches(title, "title", u"graduate, the (1967)") > 0):
                                                                                        return {"prediction":3, "error":1.65457}
                                                                                    if (term_matches(title, "title", u"graduate, the (1967)") <= 0):
                                                                                        if (term_matches(title, "title", u"edge") > 0):
                                                                                            return {"prediction":3, "error":1.51877}
                                                                                        if (term_matches(title, "title", u"edge") <= 0):
                                                                                            if (item_matches(genres, "genres", u"Drama") > 0):
                                                                                                if (zipcode is None):
                                                                                                    return {"prediction": 4.83333, "error": 1.28505}
                                                                                                if (zipcode > 22103):
                                                                                                    return {"prediction":5, "error":0.57469}
                                                                                                if (zipcode <= 22103):
                                                                                                    return {"prediction":4, "error":1.28505}
                                                                                            if (item_matches(genres, "genres", u"Drama") <= 0):
                                                                                                if (timestamp > 978227687):
                                                                                                    return {"prediction":5, "error":1.56826}
                                                                                                if (timestamp <= 978227687):
                                                                                                    return {"prediction":4, "error":0.78413}
                                                                    if (timestamp <= 978215603):
                                                                        return {"prediction":3, "error":0.58872}
                                                                if (timestamp <= 978201899):
                                                                    if (term_matches(title, "title", u"lola") > 0):
                                                                        return {"prediction":4, "error":0.91271}
                                                                    if (term_matches(title, "title", u"lola") <= 0):
                                                                        if (term_matches(title, "title", u"1984") > 0):
                                                                            return {"prediction":4, "error":0.82728}
                                                                        if (term_matches(title, "title", u"1984") <= 0):
                                                                            if (term_matches(title, "title", u"terminator") > 0):
                                                                                return {"prediction":4.5, "error":5.26764}
                                                                            if (term_matches(title, "title", u"terminator") <= 0):
                                                                                return {"prediction":5, "error":0.20738}
                if (gender == "Female"):
                    if (timestamp is None):
                        return {"prediction": 4.26316, "error": 1.16276}
                    if (timestamp > 978226722):
                        if (timestamp > 978237189):
                            if (timestamp > 978238243):
                                if (term_matches(title, "title", u"1964") > 0):
                                    return {"prediction":3, "error":1.14678}
                                if (term_matches(title, "title", u"1964") <= 0):
                                    if (term_matches(title, "title", u"1996") > 0):
                                        return {"prediction":3.5, "error":5.26764}
                                    if (term_matches(title, "title", u"1996") <= 0):
                                        if (term_matches(title, "title", u"1975") > 0):
                                            return {"prediction":5, "error":0.95727}
                                        if (term_matches(title, "title", u"1975") <= 0):
                                            if (term_matches(title, "title", u"beauty") > 0):
                                                return {"prediction":5, "error":0.91271}
                                            if (term_matches(title, "title", u"beauty") <= 0):
                                                if (timestamp > 978301752):
                                                    if (timestamp > 978302153):
                                                        return {"prediction":4, "error":0.93847}
                                                    if (timestamp <= 978302153):
                                                        if (term_matches(title, "title", u"1982") > 0):
                                                            return {"prediction":4, "error":2.93426}
                                                        if (term_matches(title, "title", u"1982") <= 0):
                                                            return {"prediction":5, "error":2.07483}
                                                if (timestamp <= 978301752):
                                                    return {"prediction":4, "error":0.31268}
                            if (timestamp <= 978238243):
                                return {"prediction":5, "error":0.82845}
                        if (timestamp <= 978237189):
                            if (item_matches(genres, "genres", u"Thriller") > 0):
                                return {"prediction":4, "error":2.03402}
                            if (item_matches(genres, "genres", u"Thriller") <= 0):
                                return {"prediction":3, "error":1.17434}
                    if (timestamp <= 978226722):
                        if (term_matches(title, "title", u"1997") > 0):
                            return {"prediction":3, "error":1.35749}
                        if (term_matches(title, "title", u"1997") <= 0):
                            if (item_matches(genres, "genres", u"Adventure") > 0):
                                if (timestamp > 978153877):
                                    return {"prediction":4, "error":2.07483}
                                if (timestamp <= 978153877):
                                    return {"prediction":5, "error":2.93426}
                            if (item_matches(genres, "genres", u"Adventure") <= 0):
                                if (timestamp > 978152601):
                                    return {"prediction":5, "error":0.25805}
                                if (timestamp <= 978152601):
                                    return {"prediction":4, "error":0.77415}


def predict(gender=None,
            age_range=None,
            occupation=None,
            zipcode=None,
            title=None,
            genres=None,
            timestamp=None):
    prediction = predict_rating(gender=gender, age_range=age_range, occupation=occupation, zipcode=zipcode, title=title, genres=genres, timestamp=timestamp)
    return prediction