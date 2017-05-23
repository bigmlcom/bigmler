
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
