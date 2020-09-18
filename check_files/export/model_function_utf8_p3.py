# -*- coding: utf-8 -*-
def predict_imagen(titulo=None,
                   grados=None,
                   ano_lanzamiento=None,
                   paginas=None,
                   codbarras=None):
    """ Predictor for Imagen from model/5a143f443980b50a74003699

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
        "titulo": {
            "case_sensitive": False,
            "token_mode": 'all',
        },
    }
    term_forms = {
        "titulo": {
            "fantásticos": ['fantásticos', 'fantásticas'],
            "gigante": ['gigante', 'gigantes'],
        },
    }

    if (codbarras is None):
        return {"prediction": 1.82, "error": 5.53698}
    if (codbarras > 9789872414340):
        if (ano_lanzamiento is None):
            return {"prediction": 9, "error": 7.02326}
        if (ano_lanzamiento > 2008):
            if (paginas is None):
                return {"prediction": 10.5, "error": 5.88884}
            if (paginas > 90):
                if (titulo is None):
                    return {"prediction": 9, "error": 5.08228}
                if (term_matches(titulo, "titulo", u"fantásticos") > 0):
                    return {"prediction":8, "error":5.08228}
                if (term_matches(titulo, "titulo", u"fantásticos") <= 0):
                    if (grados is None):
                        return {"prediction": 9.5, "error": 5.26764}
                    if (grados == "Elsa Pizzi"):
                        return {"prediction":9, "error":5.26764}
                    if (grados != "Elsa Pizzi"):
                        return {"prediction":10, "error":5.26764}
            if (paginas <= 90):
                if (titulo is None):
                    return {"prediction": 12, "error": 5.08228}
                if (term_matches(titulo, "titulo", u"gigante") > 0):
                    return {"prediction":11, "error":5.08228}
                if (term_matches(titulo, "titulo", u"gigante") <= 0):
                    if (grados is None):
                        return {"prediction": 12.5, "error": 5.26764}
                    if (grados == "Patricia Roggio"):
                        return {"prediction":13, "error":5.26764}
                    if (grados != "Patricia Roggio"):
                        return {"prediction":12, "error":5.26764}
        if (ano_lanzamiento <= 2008):
            if (grados is None):
                return {"prediction": 6, "error": 5.08228}
            if (grados == "4°, 5°"):
                return {"prediction":7, "error":5.08228}
            if (grados != "4°, 5°"):
                if (grados == "5°, 6°"):
                    return {"prediction":5, "error":5.26764}
                if (grados != "5°, 6°"):
                    return {"prediction":6, "error":5.26764}
    if (codbarras <= 9789872414340):
        if (codbarras > 9789872414309):
            if (paginas is None):
                return {"prediction": 3, "error": 5.08228}
            if (paginas > 100):
                if (grados is None):
                    return {"prediction": 2.5, "error": 5.26764}
                if (grados == "4°, 5°"):
                    return {"prediction":2, "error":5.26764}
                if (grados != "4°, 5°"):
                    return {"prediction":3, "error":5.26764}
            if (paginas <= 100):
                return {"prediction":4, "error":5.08228}
        if (codbarras <= 9789872414309):
            if (codbarras > 9789871989852):
                return {"prediction":1, "error":0.26071}
            if (codbarras <= 9789871989852):
                return {"prediction":0, "error":0.04286}


def predict(titulo=None,
            grados=None,
            ano_lanzamiento=None,
            paginas=None,
            codbarras=None):
    prediction = predict_imagen(titulo=titulo, grados=grados, ano_lanzamiento=ano_lanzamiento, paginas=paginas, codbarras=codbarras)
    return prediction
