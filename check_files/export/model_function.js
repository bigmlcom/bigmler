
/**
*  Predictor for rating
*  Created using BigMLer
*/
function predictRating(gender, age_range, occupation, zipcode, title, genres, timestamp) {

    var TERM_ANALYSIS = {
        "title": {
                "case_sensitive": false,
                "token_mode": 'all',
        },
    }
    var TERM_FORMS = {
        "title": {
            "beauty": ["beauty", "beautiful"],
            "day": ["day", "days"],
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

    var ITEM_ANALYSIS = {
        "genres": {
                "separator": '$',
        },
    }
    var escape = function(text) {
      return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
    };

    function itemMatches(text, fieldLabel, item) {
      /**
       * Computes item matches depending on the chosen item analysis options
       *
       * @param {string} text Input text
       * @param {string} fieldLabel Name of the field
       * @param {string} item Item to compare
       */

      var options = ITEM_ANALYSIS[fieldLabel];
      var separator = options.separator;
      var regexp = options.separator_regexp;
      if (typeof(regexp) === 'undefined') {
        if (typeof(separator) === 'undefined') {
          separator = " ";
        }
        regexp = escape(separator);
      }

      var pattern = new RegExp(regexp, 'g');
      var inputs = text.split(pattern);
      var counter = 0;
      for (var index = 0; index < inputs.length; index++) {
        if (inputs[index] == item) {
          counter++;
          break;
        }
      }
      return counter;
    };


    // predict body
    if (genres == null) {
        return {prediction: 3.7, error: 1.28278}}
    if (itemMatches(genres, "genres", "Comedy") > 0) {
        if (title == null) {
            return {prediction: 3.39535, error: 1.57231}}
        if (termMatches(title, "title", "life") > 0) {
            return {prediction: 5, error: 0.90777};
        }
        if (termMatches(title, "title", "life") <= 0) {
            if (termMatches(title, "title", "forrest gump (1994)") > 0) {
                return {prediction: 5, error: 1.09624};
            }
            if (termMatches(title, "title", "forrest gump (1994)") <= 0) {
                if (termMatches(title, "title", "1983") > 0) {
                    return {prediction: 5, error: 1.08292};
                }
                if (termMatches(title, "title", "1983") <= 0) {
                    if (zipcode == null) {
                        return {prediction: 3.25316, error: 1.5086}}
                    if (zipcode > 7753) {
                        if (itemMatches(genres, "genres", "Horror") > 0) {
                            if (timestamp == null) {
                                return {prediction: 2, error: 5.08228}}
                            if (timestamp > 978258115) {
                                return {prediction: 1.5, error: 5.26764};
                            }
                            if (timestamp <= 978258115) {
                                return {prediction: 3, error: 5.08228};
                            }
                        }
                        if (itemMatches(genres, "genres", "Horror") <= 0) {
                            if (timestamp == null) {
                                return {prediction: 3.3913, error: 1.43342}}
                            if (timestamp > 978218758) {
                                if (itemMatches(genres, "genres", "Thriller") > 0) {
                                    return {prediction: 2, error: 10.53528};
                                }
                                if (itemMatches(genres, "genres", "Thriller") <= 0) {
                                    if (itemMatches(genres, "genres", "Crime") > 0) {
                                        return {prediction: 5, error: 0.9578};
                                    }
                                    if (itemMatches(genres, "genres", "Crime") <= 0) {
                                        if (termMatches(title, "title", "breakfast club, the (1985)") > 0) {
                                            return {prediction: 2, error: 1.31722};
                                        }
                                        if (termMatches(title, "title", "breakfast club, the (1985)") <= 0) {
                                            if (termMatches(title, "title", "monty") > 0) {
                                                return {prediction: 2, error: 1.28344};
                                            }
                                            if (termMatches(title, "title", "monty") <= 0) {
                                                if (termMatches(title, "title", "stand by me (1986)") > 0) {
                                                    return {prediction: 5, error: 1.24322};
                                                }
                                                if (termMatches(title, "title", "stand by me (1986)") <= 0) {
                                                    if (timestamp > 978228710) {
                                                        if (itemMatches(genres, "genres", "Musical") > 0) {
                                                            return {prediction: 4.5, error: 5.26764};
                                                        }
                                                        if (itemMatches(genres, "genres", "Musical") <= 0) {
                                                            if (itemMatches(genres, "genres", "Romance") > 0) {
                                                                if (termMatches(title, "title", "day") > 0) {
                                                                    return {prediction: 2, error: 1.38964};
                                                                }
                                                                if (termMatches(title, "title", "day") <= 0) {
                                                                    if (timestamp > 978428301) {
                                                                        return {prediction: 4, error: 1.13085};
                                                                    }
                                                                    if (timestamp <= 978428301) {
                                                                        if (termMatches(title, "title", "shakespeare in love (1998)") > 0) {
                                                                            return {prediction: 4, error: 0.958};
                                                                        }
                                                                        if (termMatches(title, "title", "shakespeare in love (1998)") <= 0) {
                                                                            return {prediction: 3, error: 0.36209};
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                            if (itemMatches(genres, "genres", "Romance") <= 0) {
                                                                if (occupation == null) {
                                                                    return {prediction: 3.65385, error: 1.31541}}
                                                                if (occupation == "writer") {
                                                                    return {prediction: 5, error: 1.31541};
                                                                }
                                                                if (occupation != "writer") {
                                                                    if (itemMatches(genres, "genres", "Drama") > 0) {
                                                                        if (termMatches(title, "title", "1997") > 0) {
                                                                            return {prediction: 5, error: 1.56826};
                                                                        }
                                                                        if (termMatches(title, "title", "1997") <= 0) {
                                                                            return {prediction: 4, error: 0.78413};
                                                                        }
                                                                    }
                                                                    if (itemMatches(genres, "genres", "Drama") <= 0) {
                                                                        if (timestamp > 978298248) {
                                                                            if (timestamp > 978298391) {
                                                                                if (gender == null) {
                                                                                    return {prediction: 3.6, error: 1.92072}}
                                                                                if (gender == "Female") {
                                                                                    return {prediction: 4, error: 1.35815};
                                                                                }
                                                                                if (gender == "Male") {
                                                                                    if (termMatches(title, "title", "1996") > 0) {
                                                                                        return {prediction: 4, error: 2.93426};
                                                                                    }
                                                                                    if (termMatches(title, "title", "1996") <= 0) {
                                                                                        return {prediction: 3, error: 2.07483};
                                                                                    }
                                                                                }
                                                                            }
                                                                            if (timestamp <= 978298391) {
                                                                                return {prediction: 5, error: 2.36951};
                                                                            }
                                                                        }
                                                                        if (timestamp <= 978298248) {
                                                                            if (termMatches(title, "title", "1980") > 0) {
                                                                                return {prediction: 2, error: 1.31017};
                                                                            }
                                                                            if (termMatches(title, "title", "1980") <= 0) {
                                                                                if (timestamp > 978297750) {
                                                                                    if (termMatches(title, "title", "1999") > 0) {
                                                                                        return {prediction: 3, error: 1.14938};
                                                                                    }
                                                                                    if (termMatches(title, "title", "1999") <= 0) {
                                                                                        return {prediction: 4, error: 0.81274};
                                                                                    }
                                                                                }
                                                                                if (timestamp <= 978297750) {
                                                                                    if (termMatches(title, "title", "1994") > 0) {
                                                                                        return {prediction: 4, error: 1.09476};
                                                                                    }
                                                                                    if (termMatches(title, "title", "1994") <= 0) {
                                                                                        return {prediction: 3, error: 0.44694};
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                    if (timestamp <= 978228710) {
                                                        if (timestamp > 978226820) {
                                                            return {prediction: 5, error: 2.93426};
                                                        }
                                                        if (timestamp <= 978226820) {
                                                            return {prediction: 4, error: 2.07483};
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            if (timestamp <= 978218758) {
                                if (termMatches(title, "title", "1994") > 0) {
                                    return {prediction: 1, error: 1.96692};
                                }
                                if (termMatches(title, "title", "1994") <= 0) {
                                    if (timestamp > 978174603) {
                                        if (termMatches(title, "title", "1999") > 0) {
                                            if (timestamp > 978200667) {
                                                return {prediction: 1, error: 3.89486};
                                            }
                                            if (timestamp <= 978200667) {
                                                if (timestamp > 978196617) {
                                                    return {prediction: 3, error: 2.07483};
                                                }
                                                if (timestamp <= 978196617) {
                                                    return {prediction: 2, error: 2.93426};
                                                }
                                            }
                                        }
                                        if (termMatches(title, "title", "1999") <= 0) {
                                            if (occupation == null) {
                                                return {prediction: 3.09091, error: 1.95519}}
                                            if (occupation == "executive/managerial") {
                                                return {prediction: 4, error: 1.38253};
                                            }
                                            if (occupation != "executive/managerial") {
                                                if (timestamp > 978200651) {
                                                    if (termMatches(title, "title", "bride") > 0) {
                                                        return {prediction: 2, error: 2.36951};
                                                    }
                                                    if (termMatches(title, "title", "bride") <= 0) {
                                                        if (timestamp > 978202404) {
                                                            return {prediction: 3, error: 1.35815};
                                                        }
                                                        if (timestamp <= 978202404) {
                                                            if (termMatches(title, "title", "batman") > 0) {
                                                                return {prediction: 3, error: 2.93426};
                                                            }
                                                            if (termMatches(title, "title", "batman") <= 0) {
                                                                return {prediction: 4, error: 2.07483};
                                                            }
                                                        }
                                                    }
                                                }
                                                if (timestamp <= 978200651) {
                                                    if (itemMatches(genres, "genres", "Romance") > 0) {
                                                        return {prediction: 3, error: 2.93426};
                                                    }
                                                    if (itemMatches(genres, "genres", "Romance") <= 0) {
                                                        return {prediction: 2, error: 2.07483};
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    if (timestamp <= 978174603) {
                                        if (termMatches(title, "title", "1985") > 0) {
                                            return {prediction: 5, error: 2.93395};
                                        }
                                        if (termMatches(title, "title", "1985") <= 0) {
                                            if (occupation == null) {
                                                return {prediction: 3.5, error: 2.34869}}
                                            if (occupation == "sales/marketing") {
                                                return {prediction: 4, error: 2.34869};
                                            }
                                            if (occupation != "sales/marketing") {
                                                if (timestamp > 978174551) {
                                                    return {prediction: 4, error: 2.93426};
                                                }
                                                if (timestamp <= 978174551) {
                                                    return {prediction: 3, error: 2.07483};
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if (zipcode <= 7753) {
                        if (itemMatches(genres, "genres", "Drama") > 0) {
                            return {prediction: 4, error: 2.60606};
                        }
                        if (itemMatches(genres, "genres", "Drama") <= 0) {
                            if (timestamp == null) {
                                return {prediction: 1.8, error: 2.93395}}
                            if (timestamp > 978904214) {
                                if (termMatches(title, "title", "1997") > 0) {
                                    return {prediction: 3, error: 2.93426};
                                }
                                if (termMatches(title, "title", "1997") <= 0) {
                                    return {prediction: 2, error: 2.07483};
                                }
                            }
                            if (timestamp <= 978904214) {
                                return {prediction: 1, error: 2.07461};
                            }
                        }
                    }
                }
            }
        }
    }
    if (itemMatches(genres, "genres", "Comedy") <= 0) {
        if (title == null) {
            return {prediction: 3.82843, error: 1.25974}}
        if (termMatches(title, "title", "1995") > 0) {
            if (occupation == null) {
                return {prediction: 2.66667, error: 3.25095}}
            if (occupation == "clerical/admin") {
                return {prediction: 1, error: 3.25095};
            }
            if (occupation != "clerical/admin") {
                if (itemMatches(genres, "genres", "Romance") > 0) {
                    return {prediction: 4, error: 2.47964};
                }
                if (itemMatches(genres, "genres", "Romance") <= 0) {
                    if (occupation == "writer") {
                        return {prediction: 2, error: 2.03402};
                    }
                    if (occupation != "writer") {
                        return {prediction: 3, error: 1.17434};
                    }
                }
            }
        }
        if (termMatches(title, "title", "1995") <= 0) {
            if (itemMatches(genres, "genres", "Horror") > 0) {
                if (timestamp == null) {
                    return {prediction: 3.35, error: 2.2498}}
                if (timestamp > 978200824) {
                    if (timestamp > 978876267) {
                        return {prediction: 2, error: 1.97983};
                    }
                    if (timestamp <= 978876267) {
                        if (itemMatches(genres, "genres", "Thriller") > 0) {
                            if (termMatches(title, "title", "alien") > 0) {
                                return {prediction: 4, error: 2.93426};
                            }
                            if (termMatches(title, "title", "alien") <= 0) {
                                return {prediction: 3, error: 2.07483};
                            }
                        }
                        if (itemMatches(genres, "genres", "Thriller") <= 0) {
                            if (timestamp > 978268588) {
                                if (termMatches(title, "title", "king") > 0) {
                                    return {prediction: 4, error: 2.03402};
                                }
                                if (termMatches(title, "title", "king") <= 0) {
                                    return {prediction: 5, error: 1.17434};
                                }
                            }
                            if (timestamp <= 978268588) {
                                if (termMatches(title, "title", "alien") > 0) {
                                    return {prediction: 3, error: 1.56826};
                                }
                                if (termMatches(title, "title", "alien") <= 0) {
                                    return {prediction: 4, error: 0.78413};
                                }
                            }
                        }
                    }
                }
                if (timestamp <= 978200824) {
                    if (occupation == null) {
                        return {prediction: 2.42857, error: 3.28429}}
                    if (occupation == "academic/educator") {
                        if (termMatches(title, "title", "1960") > 0) {
                            return {prediction: 4, error: 2.93426};
                        }
                        if (termMatches(title, "title", "1960") <= 0) {
                            return {prediction: 3, error: 2.07483};
                        }
                    }
                    if (occupation != "academic/educator") {
                        if (termMatches(title, "title", "bringing") > 0) {
                            return {prediction: 3, error: 3.89486};
                        }
                        if (termMatches(title, "title", "bringing") <= 0) {
                            if (timestamp > 978200492) {
                                return {prediction: 2, error: 2.93426};
                            }
                            if (timestamp <= 978200492) {
                                return {prediction: 1, error: 2.07483};
                            }
                        }
                    }
                }
            }
            if (itemMatches(genres, "genres", "Horror") <= 0) {
                if (gender == null) {
                    return {prediction: 3.92135, error: 1.21004}}
                if (gender == "Male") {
                    if (termMatches(title, "title", "dick tracy (1990)") > 0) {
                        return {prediction: 1, error: 1.29316};
                    }
                    if (termMatches(title, "title", "dick tracy (1990)") <= 0) {
                        if (occupation == null) {
                            return {prediction: 3.84892, error: 1.26101}}
                        if (occupation == "writer") {
                            if (timestamp == null) {
                                return {prediction: 3.2, error: 2.52836}}
                            if (timestamp > 978243869) {
                                if (itemMatches(genres, "genres", "Romance") > 0) {
                                    return {prediction: 4, error: 2.5701};
                                }
                                if (itemMatches(genres, "genres", "Romance") <= 0) {
                                    if (timestamp > 978246320) {
                                        if (timestamp > 978246556) {
                                            return {prediction: 2, error: 2.93426};
                                        }
                                        if (timestamp <= 978246556) {
                                            return {prediction: 3, error: 2.07483};
                                        }
                                    }
                                    if (timestamp <= 978246320) {
                                        return {prediction: 2, error: 1.35815};
                                    }
                                }
                            }
                            if (timestamp <= 978243869) {
                                if (termMatches(title, "title", "1994") > 0) {
                                    return {prediction: 3, error: 3.32155};
                                }
                                if (termMatches(title, "title", "1994") <= 0) {
                                    if (itemMatches(genres, "genres", "Film-Noir") > 0) {
                                        return {prediction: 4, error: 2.93426};
                                    }
                                    if (itemMatches(genres, "genres", "Film-Noir") <= 0) {
                                        return {prediction: 4.5, error: 5.26764};
                                    }
                                }
                            }
                        }
                        if (occupation != "writer") {
                            if (termMatches(title, "title", "2000") > 0) {
                                if (termMatches(title, "title", "mission") > 0) {
                                    return {prediction: 2.5, error: 5.26764};
                                }
                                if (termMatches(title, "title", "mission") <= 0) {
                                    if (termMatches(title, "title", "cell") > 0) {
                                        return {prediction: 3, error: 1.09476};
                                    }
                                    if (termMatches(title, "title", "cell") <= 0) {
                                        if (timestamp == null) {
                                            return {prediction: 3.6, error: 1.92072}}
                                        if (timestamp > 978217782) {
                                            return {prediction: 3, error: 1.35815};
                                        }
                                        if (timestamp <= 978217782) {
                                            return {prediction: 4, error: 1.10893};
                                        }
                                    }
                                }
                            }
                            if (termMatches(title, "title", "2000") <= 0) {
                                if (timestamp == null) {
                                    return {prediction: 3.95, error: 1.26219}}
                                if (timestamp > 978298955) {
                                    if (timestamp > 1009669148) {
                                        if (termMatches(title, "title", "1997") > 0) {
                                            return {prediction: 5, error: 2.93426};
                                        }
                                        if (termMatches(title, "title", "1997") <= 0) {
                                            return {prediction: 4, error: 2.07483};
                                        }
                                    }
                                    if (timestamp <= 1009669148) {
                                        if (termMatches(title, "title", "1989") > 0) {
                                            return {prediction: 5, error: 1.59717};
                                        }
                                        if (termMatches(title, "title", "1989") <= 0) {
                                            if (termMatches(title, "title", "1990") > 0) {
                                                return {prediction: 2, error: 1.16977};
                                            }
                                            if (termMatches(title, "title", "1990") <= 0) {
                                                if (itemMatches(genres, "genres", "Film-Noir") > 0) {
                                                    return {prediction: 4, error: 0.95152};
                                                }
                                                if (itemMatches(genres, "genres", "Film-Noir") <= 0) {
                                                    if (termMatches(title, "title", "1980") > 0) {
                                                        return {prediction: 4, error: 0.77415};
                                                    }
                                                    if (termMatches(title, "title", "1980") <= 0) {
                                                        return {prediction: 3, error: 0.25805};
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                if (timestamp <= 978298955) {
                                    if (termMatches(title, "title", "1987") > 0) {
                                        return {prediction: 1, error: 1.28682};
                                    }
                                    if (termMatches(title, "title", "1987") <= 0) {
                                        if (termMatches(title, "title", "fight") > 0) {
                                            return {prediction: 2, error: 1.23008};
                                        }
                                        if (termMatches(title, "title", "fight") <= 0) {
                                            if (termMatches(title, "title", "1993") > 0) {
                                                if (timestamp > 978234034) {
                                                    return {prediction: 4, error: 0.89387};
                                                }
                                                if (timestamp <= 978234034) {
                                                    return {prediction: 3, error: 0.77411};
                                                }
                                            }
                                            if (termMatches(title, "title", "1993") <= 0) {
                                                if (termMatches(title, "title", "1996") > 0) {
                                                    if (occupation == "other") {
                                                        return {prediction: 1, error: 2.43201};
                                                    }
                                                    if (occupation != "other") {
                                                        if (itemMatches(genres, "genres", "Drama") > 0) {
                                                            return {prediction: 5, error: 1.38965};
                                                        }
                                                        if (itemMatches(genres, "genres", "Drama") <= 0) {
                                                            if (zipcode == null) {
                                                                return {prediction: 3.75, error: 1.96736}}
                                                            if (zipcode > 94327) {
                                                                return {prediction: 5, error: 1.96736};
                                                            }
                                                            if (zipcode <= 94327) {
                                                                if (itemMatches(genres, "genres", "Thriller") > 0) {
                                                                    return {prediction: 5, error: 1.90304};
                                                                }
                                                                if (itemMatches(genres, "genres", "Thriller") <= 0) {
                                                                    if (occupation == "executive/managerial") {
                                                                        return {prediction: 3, error: 10.53528};
                                                                    }
                                                                    if (occupation != "executive/managerial") {
                                                                        if (zipcode > 58365) {
                                                                            return {prediction: 3, error: 0.99163};
                                                                        }
                                                                        if (zipcode <= 58365) {
                                                                            if (timestamp > 978297836) {
                                                                                return {prediction: 3, error: 1.28505};
                                                                            }
                                                                            if (timestamp <= 978297836) {
                                                                                return {prediction: 4, error: 0.57469};
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                                if (termMatches(title, "title", "1996") <= 0) {
                                                    if (termMatches(title, "title", "negotiator") > 0) {
                                                        return {prediction: 3, error: 0.82118};
                                                    }
                                                    if (termMatches(title, "title", "negotiator") <= 0) {
                                                        if (itemMatches(genres, "genres", "War") > 0) {
                                                            if (timestamp > 978201771) {
                                                                if (timestamp > 978294214) {
                                                                    if (timestamp > 978295884) {
                                                                        return {prediction: 4, error: 2.07483};
                                                                    }
                                                                    if (timestamp <= 978295884) {
                                                                        return {prediction: 5, error: 2.93426};
                                                                    }
                                                                }
                                                                if (timestamp <= 978294214) {
                                                                    if (timestamp > 978211160) {
                                                                        if (timestamp > 978294061) {
                                                                            return {prediction: 2, error: 2.03402};
                                                                        }
                                                                        if (timestamp <= 978294061) {
                                                                            return {prediction: 3, error: 1.17434};
                                                                        }
                                                                    }
                                                                    if (timestamp <= 978211160) {
                                                                        return {prediction: 4, error: 2.47964};
                                                                    }
                                                                }
                                                            }
                                                            if (timestamp <= 978201771) {
                                                                return {prediction: 5, error: 2.56453};
                                                            }
                                                        }
                                                        if (itemMatches(genres, "genres", "War") <= 0) {
                                                            if (occupation == "K-12 student") {
                                                                if (timestamp > 978146981) {
                                                                    return {prediction: 4, error: 2.93426};
                                                                }
                                                                if (timestamp <= 978146981) {
                                                                    return {prediction: 3, error: 2.07483};
                                                                }
                                                            }
                                                            if (occupation != "K-12 student") {
                                                                if (timestamp > 978201899) {
                                                                    if (timestamp > 978215603) {
                                                                        if (itemMatches(genres, "genres", "Adventure") > 0) {
                                                                            if (zipcode == null) {
                                                                                return {prediction: 4.72727, error: 1.09872}}
                                                                            if (zipcode > 22103) {
                                                                                if (termMatches(title, "title", "1994") > 0) {
                                                                                    return {prediction: 4, error: 1.72408};
                                                                                }
                                                                                if (termMatches(title, "title", "1994") <= 0) {
                                                                                    if (termMatches(title, "title", "king") > 0) {
                                                                                        return {prediction: 4, error: 1.92072};
                                                                                    }
                                                                                    if (termMatches(title, "title", "king") <= 0) {
                                                                                        if (termMatches(title, "title", "jones") > 0) {
                                                                                            return {prediction: 4, error: 2.03402};
                                                                                        }
                                                                                        if (termMatches(title, "title", "jones") <= 0) {
                                                                                            return {prediction: 5, error: 1.17434};
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                            if (zipcode <= 22103) {
                                                                                return {prediction: 5, error: 0.49136};
                                                                            }
                                                                        }
                                                                        if (itemMatches(genres, "genres", "Adventure") <= 0) {
                                                                            if (timestamp > 978294097) {
                                                                                if (termMatches(title, "title", "1960") > 0) {
                                                                                    return {prediction: 3, error: 1.25106};
                                                                                }
                                                                                if (termMatches(title, "title", "1960") <= 0) {
                                                                                    if (timestamp > 978294245) {
                                                                                        if (timestamp > 978298584) {
                                                                                            return {prediction: 5, error: 0.80826};
                                                                                        }
                                                                                        if (timestamp <= 978298584) {
                                                                                            if (termMatches(title, "title", "terminator") > 0) {
                                                                                                return {prediction: 5, error: 1.18675};
                                                                                            }
                                                                                            if (termMatches(title, "title", "terminator") <= 0) {
                                                                                                if (termMatches(title, "title", "1994") > 0) {
                                                                                                    return {prediction: 5, error: 1.18253};
                                                                                                }
                                                                                                if (termMatches(title, "title", "1994") <= 0) {
                                                                                                    if (occupation == "scientist") {
                                                                                                        return {prediction: 5, error: 1.13085};
                                                                                                    }
                                                                                                    if (occupation != "scientist") {
                                                                                                        if (termMatches(title, "title", "1976") > 0) {
                                                                                                            return {prediction: 5, error: 0.958};
                                                                                                        }
                                                                                                        if (termMatches(title, "title", "1976") <= 0) {
                                                                                                            return {prediction: 4, error: 0.36209};
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                    if (timestamp <= 978294245) {
                                                                                        return {prediction: 5, error: 0.60498};
                                                                                    }
                                                                                }
                                                                            }
                                                                            if (timestamp <= 978294097) {
                                                                                if (timestamp > 978230086) {
                                                                                    if (timestamp > 978234842) {
                                                                                        return {prediction: 4, error: 1.09476};
                                                                                    }
                                                                                    if (timestamp <= 978234842) {
                                                                                        if (termMatches(title, "title", "truman") > 0) {
                                                                                            return {prediction: 4, error: 1.56826};
                                                                                        }
                                                                                        if (termMatches(title, "title", "truman") <= 0) {
                                                                                            return {prediction: 3, error: 0.78413};
                                                                                        }
                                                                                    }
                                                                                }
                                                                                if (timestamp <= 978230086) {
                                                                                    if (termMatches(title, "title", "graduate, the (1967)") > 0) {
                                                                                        return {prediction: 3, error: 1.65457};
                                                                                    }
                                                                                    if (termMatches(title, "title", "graduate, the (1967)") <= 0) {
                                                                                        if (termMatches(title, "title", "edge") > 0) {
                                                                                            return {prediction: 3, error: 1.51877};
                                                                                        }
                                                                                        if (termMatches(title, "title", "edge") <= 0) {
                                                                                            if (itemMatches(genres, "genres", "Drama") > 0) {
                                                                                                if (zipcode == null) {
                                                                                                    return {prediction: 4.83333, error: 1.28505}}
                                                                                                if (zipcode > 22103) {
                                                                                                    return {prediction: 5, error: 0.57469};
                                                                                                }
                                                                                                if (zipcode <= 22103) {
                                                                                                    return {prediction: 4, error: 1.28505};
                                                                                                }
                                                                                            }
                                                                                            if (itemMatches(genres, "genres", "Drama") <= 0) {
                                                                                                if (timestamp > 978227687) {
                                                                                                    return {prediction: 5, error: 1.56826};
                                                                                                }
                                                                                                if (timestamp <= 978227687) {
                                                                                                    return {prediction: 4, error: 0.78413};
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                    if (timestamp <= 978215603) {
                                                                        return {prediction: 3, error: 0.58872};
                                                                    }
                                                                }
                                                                if (timestamp <= 978201899) {
                                                                    if (termMatches(title, "title", "lola") > 0) {
                                                                        return {prediction: 4, error: 0.91271};
                                                                    }
                                                                    if (termMatches(title, "title", "lola") <= 0) {
                                                                        if (termMatches(title, "title", "1984") > 0) {
                                                                            return {prediction: 4, error: 0.82728};
                                                                        }
                                                                        if (termMatches(title, "title", "1984") <= 0) {
                                                                            if (termMatches(title, "title", "terminator") > 0) {
                                                                                return {prediction: 4.5, error: 5.26764};
                                                                            }
                                                                            if (termMatches(title, "title", "terminator") <= 0) {
                                                                                return {prediction: 5, error: 0.20738};
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                if (gender == "Female") {
                    if (timestamp == null) {
                        return {prediction: 4.26316, error: 1.16276}}
                    if (timestamp > 978226722) {
                        if (timestamp > 978237189) {
                            if (timestamp > 978238243) {
                                if (termMatches(title, "title", "1964") > 0) {
                                    return {prediction: 3, error: 1.14678};
                                }
                                if (termMatches(title, "title", "1964") <= 0) {
                                    if (termMatches(title, "title", "1996") > 0) {
                                        return {prediction: 3.5, error: 5.26764};
                                    }
                                    if (termMatches(title, "title", "1996") <= 0) {
                                        if (termMatches(title, "title", "1975") > 0) {
                                            return {prediction: 5, error: 0.95727};
                                        }
                                        if (termMatches(title, "title", "1975") <= 0) {
                                            if (termMatches(title, "title", "beauty") > 0) {
                                                return {prediction: 5, error: 0.91271};
                                            }
                                            if (termMatches(title, "title", "beauty") <= 0) {
                                                if (timestamp > 978301752) {
                                                    if (timestamp > 978302153) {
                                                        return {prediction: 4, error: 0.93847};
                                                    }
                                                    if (timestamp <= 978302153) {
                                                        if (termMatches(title, "title", "1982") > 0) {
                                                            return {prediction: 4, error: 2.93426};
                                                        }
                                                        if (termMatches(title, "title", "1982") <= 0) {
                                                            return {prediction: 5, error: 2.07483};
                                                        }
                                                    }
                                                }
                                                if (timestamp <= 978301752) {
                                                    return {prediction: 4, error: 0.31268};
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            if (timestamp <= 978238243) {
                                return {prediction: 5, error: 0.82845};
                            }
                        }
                        if (timestamp <= 978237189) {
                            if (itemMatches(genres, "genres", "Thriller") > 0) {
                                return {prediction: 4, error: 2.03402};
                            }
                            if (itemMatches(genres, "genres", "Thriller") <= 0) {
                                return {prediction: 3, error: 1.17434};
                            }
                        }
                    }
                    if (timestamp <= 978226722) {
                        if (termMatches(title, "title", "1997") > 0) {
                            return {prediction: 3, error: 1.35749};
                        }
                        if (termMatches(title, "title", "1997") <= 0) {
                            if (itemMatches(genres, "genres", "Adventure") > 0) {
                                if (timestamp > 978153877) {
                                    return {prediction: 4, error: 2.07483};
                                }
                                if (timestamp <= 978153877) {
                                    return {prediction: 5, error: 2.93426};
                                }
                            }
                            if (itemMatches(genres, "genres", "Adventure") <= 0) {
                                if (timestamp > 978152601) {
                                    return {prediction: 5, error: 0.25805};
                                }
                                if (timestamp <= 978152601) {
                                    return {prediction: 4, error: 0.77415};
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return null;
}
