

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
