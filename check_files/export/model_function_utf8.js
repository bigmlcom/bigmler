
/**
*  Predictor for Imagen
*  Created using BigMLer
*/
function predictImagen(data) {

    var TERM_ANALYSIS = {
        "titulo": {
                "case_sensitive": false,
                "token_mode": 'all',
        },
    }
    var TERM_FORMS = {
        "titulo": {
            "fantásticos": ["fantásticos", "fantásticas"],
            "gigante": ["gigante", "gigantes"],
        },

    }


    var TM_TOKENS = 'tokens_only', TM_FULL_TERM = 'full_terms_only',
      TM_ALL = 'all';
    var FULL_TERM_PATTERN = new RegExp('^.+\b.+$');

    function termMatches(text, fieldLabel, term) {
      /**
       * Computes term matches depending on the chosen text analysis options
       *
       * @param {string} text Input text
       * @param {string} fieldLabel Name of the field
       * @param {string} term Term to compare
       */

      var options = TERM_ANALYSIS[fieldLabel];
      var fieldTerms = TERM_FORMS[fieldLabel];
      var terms = (typeof fieldTerms[term] === 'undefined') ?
          [term] : fieldTerms[term];
      var tokenMode = options['token_mode'];
      var caseSensitive = options['case_sensitive'];
      var firstTerm = terms[0];
      if (tokenMode === TM_FULL_TERM) {
        return fullTermMatch(text, firstTerm, caseSensitive);
      }
      if (tokenMode === TM_ALL && terms.length == 1) {
        if (firstTerm.match(FULL_TERM_PATTERN)) {
           return fullTermMatch(text, firstTerm, caseSensitive);
        }
      }
      return termMatchesTokens(text, terms, caseSensitive);
    };


    function fullTermMatch(text, fullTerm, caseSensitive) {
      /**
       * Counts the match for full terms according to the caseSensitive option
       *
       * @param {string} text Input text
       * @param {string} fullTerm String to match
       * @param {boolean} caseSensitive Text analysis case_sensitive option
       */

      if (!caseSensitive) {
        text = text.toLowerCase();
        fullTerm = fullTerm.toLowerCase();
      }
      return (text == fullTerm) ? 1 : 0;
    }

    function getTokensFlags(caseSensitive) {
      /**
       * Modifiers for RegExp matching according to case_sensitive option
       *
       * @param {boolean} caseSensitive Text analysis case_sensitive option
       */
      var flags = 'g';
      if (!caseSensitive) {
        flags += 'i';
      }
      return flags;
    }


    function termMatchesTokens(text, terms, caseSensitive) {
      /**
       * Computes term matches depending on the chosen text analysis options
       *
       * @param {string} text Input text
       * @param {array} terms String array of terms to match
       * @param {boolean} caseSensitive Text analysis case_sensitive option
       */

      var flags = getTokensFlags(caseSensitive);
      var terms = terms.join('(\\b|_)|(\\b|_)');
      var pattern = new RegExp('(\\b|_)' + terms + '(\\b|_)', flags);
      var matches = text.match(pattern);
      return (matches == null) ? 0 : matches.length;
    }
    if (data.codBarras == null) {
        return {prediction: 1.82, error: 5.53698}}
    if (data.codBarras > 9789872414340) {
        if (data.anoLanzamiento == null) {
            return {prediction: 9, error: 7.02326}}
        if (data.anoLanzamiento > 2008) {
            if (data.paginas == null) {
                return {prediction: 10.5, error: 5.88884}}
            if (data.paginas > 90) {
                if (data.titulo == null) {
                    return {prediction: 9, error: 5.08228}}
                if (termMatches(data.titulo, "titulo", "fantásticos") > 0) {
                    return {prediction: 8, error: 5.08228};
                }
                if (termMatches(data.titulo, "titulo", "fantásticos") <= 0) {
                    if (data.grados == null) {
                        return {prediction: 9.5, error: 5.26764}}
                    if (data.grados == "Elsa Pizzi") {
                        return {prediction: 9, error: 5.26764};
                    }
                    if (data.grados != "Elsa Pizzi") {
                        return {prediction: 10, error: 5.26764};
                    }
                }
            }
            if (data.paginas <= 90) {
                if (data.titulo == null) {
                    return {prediction: 12, error: 5.08228}}
                if (termMatches(data.titulo, "titulo", "gigante") > 0) {
                    return {prediction: 11, error: 5.08228};
                }
                if (termMatches(data.titulo, "titulo", "gigante") <= 0) {
                    if (data.grados == null) {
                        return {prediction: 12.5, error: 5.26764}}
                    if (data.grados == "Patricia Roggio") {
                        return {prediction: 13, error: 5.26764};
                    }
                    if (data.grados != "Patricia Roggio") {
                        return {prediction: 12, error: 5.26764};
                    }
                }
            }
        }
        if (data.anoLanzamiento <= 2008) {
            if (data.grados == null) {
                return {prediction: 6, error: 5.08228}}
            if (data.grados == "4°, 5°") {
                return {prediction: 7, error: 5.08228};
            }
            if (data.grados != "4°, 5°") {
                if (data.grados == "5°, 6°") {
                    return {prediction: 5, error: 5.26764};
                }
                if (data.grados != "5°, 6°") {
                    return {prediction: 6, error: 5.26764};
                }
            }
        }
    }
    if (data.codBarras <= 9789872414340) {
        if (data.codBarras > 9789872414309) {
            if (data.paginas == null) {
                return {prediction: 3, error: 5.08228}}
            if (data.paginas > 100) {
                if (data.grados == null) {
                    return {prediction: 2.5, error: 5.26764}}
                if (data.grados == "4°, 5°") {
                    return {prediction: 2, error: 5.26764};
                }
                if (data.grados != "4°, 5°") {
                    return {prediction: 3, error: 5.26764};
                }
            }
            if (data.paginas <= 100) {
                return {prediction: 4, error: 5.08228};
            }
        }
        if (data.codBarras <= 9789872414309) {
            if (data.codBarras > 9789871989852) {
                return {prediction: 1, error: 0.26071};
            }
            if (data.codBarras <= 9789871989852) {
                return {prediction: 0, error: 0.04286};
            }
        }
    }
    return null;
}
