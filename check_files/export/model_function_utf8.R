# Predictor for Imagen
#
#        Created using BigMLer
#
predictImagen <- function(isbn=NA,
                          titulo=NA,
                          grados=NA,
                          coleccion=NA,
                          ano_lanzamiento=NA,
                          paginas=NA,
                          interior=NA,
                          tamano=NA,
                          precio=NA,
                          codbarras=NA,
                          imagen=NA){

    TERM_ANALYSIS <- list(
        "titulo"=list(
                "case_sensitive"= FALSE,
                "token_mode"= 'all'
        )
    )
    TERM_FORMS <- list(
        "titulo"=list(
            "fantásticos"=list("fantásticos", "fantásticas"),
            "gigante"=list("gigante", "gigantes")
        )
    )

    TM_TOKENS <- "tokens_only"
    TM_FULL_TERM <- "full_terms_only"
    TM_ALL <- "all"
    FULL_TERM_PATTERN <- '^.+\\b.+$'

    termMatches <- function (text, fieldLabel, term) {

      # Computes term matches depending on the chosen text analysis options
      #
      # @param {string} text Input text
      # @param {string} fieldLabel Name of the field
      # @param {string} term Term to compare

      if (is.na(text))
        return(0)
      options <- TERM_ANALYSIS[[fieldLabel]]
      fieldTerms <- TERM_FORMS[[fieldLabel]]
      tokenMode <- options[['token_mode']]
      caseSensitive <- !is.null(options[['case_sensitive']]) && options[['case_sensitive']]
      if (!caseSensitive) {
        text <- tolower(text)
        term <- tolower(term)
      }
      terms <- if (is.null(fieldTerms[[term]]))
          list(term) else fieldTerms[[term]]
      firstTerm <- terms[[1]]
      if (tokenMode == TM_FULL_TERM) {
        return(fullTermMatch(text, firstTerm))
      }
      if (tokenMode == TM_ALL && lengths(terms) == 1) {
        if (regexpr(FULL_TERM_PATTERN, firstTerm, perl=TRUE) > 0) {
          # full term match in 'all' token mode
          return(if (text == firstTerm) 1 else 0)
        }
      }
      return(termMatchesTokens(text, terms))
    }

    termMatchesTokens <- function (text, terms) {

      # Computes term matches depending on the chosen text analysis options
      #
      # @param {string} text Input text
      # @param {array} terms String array of terms to match

      terms <- paste(terms, collapse='(\\b|_)|(\\b|_)')
      pattern <- paste('(\\b|_)', terms, '(\\b|_)', sep="")
      matches <- gregexpr(pattern, text , perl=TRUE)
      if (matches < 0)
        return(0)
      return(lengths(matches))
    }
    if (is.na(codbarras)){
        return(list(prediction=1.82, error=5.53698))
    }
    if (codbarras > 9789872414340) {
        if (is.na(ano_lanzamiento)){
            return(list(prediction=9, error=7.02326))
        }
        if (ano_lanzamiento > 2008) {
            if (is.na(paginas)){
                return(list(prediction=10.5, error=5.88884))
            }
            if (paginas > 90) {
                if (termMatches(titulo, "titulo", "fantásticos")>0) {
                    return(list(prediction=8, error=5.08228))
                }
                if (termMatches(titulo, "titulo", "fantásticos")<=0) {
                    if (is.na(grados)){
                        return(list(prediction=9.5, error=5.26764))
                    }
                    if (grados == "Elsa Pizzi") {
                        return(list(prediction=9, error=5.26764))
                    }
                    if (grados != "Elsa Pizzi") {
                        return(list(prediction=10, error=5.26764))
                    }
                }
            }
            if (paginas <= 90) {
                if (termMatches(titulo, "titulo", "gigante")>0) {
                    return(list(prediction=11, error=5.08228))
                }
                if (termMatches(titulo, "titulo", "gigante")<=0) {
                    if (is.na(grados)){
                        return(list(prediction=12.5, error=5.26764))
                    }
                    if (grados == "Patricia Roggio") {
                        return(list(prediction=13, error=5.26764))
                    }
                    if (grados != "Patricia Roggio") {
                        return(list(prediction=12, error=5.26764))
                    }
                }
            }
        }
        if (ano_lanzamiento <= 2008) {
            if (is.na(grados)){
                return(list(prediction=6, error=5.08228))
            }
            if (grados == "4°, 5°") {
                return(list(prediction=7, error=5.08228))
            }
            if (grados != "4°, 5°") {
                if (grados == "5°, 6°") {
                    return(list(prediction=5, error=5.26764))
                }
                if (grados != "5°, 6°") {
                    return(list(prediction=6, error=5.26764))
                }
            }
        }
    }
    if (codbarras <= 9789872414340) {
        if (codbarras > 9789872414309) {
            if (is.na(paginas)){
                return(list(prediction=3, error=5.08228))
            }
            if (paginas > 100) {
                if (is.na(grados)){
                    return(list(prediction=2.5, error=5.26764))
                }
                if (grados == "4°, 5°") {
                    return(list(prediction=2, error=5.26764))
                }
                if (grados != "4°, 5°") {
                    return(list(prediction=3, error=5.26764))
                }
            }
            if (paginas <= 100) {
                return(list(prediction=4, error=5.08228))
            }
        }
        if (codbarras <= 9789872414309) {
            if (codbarras > 9789871989852) {
                return(list(prediction=1, error=0.26071))
            }
            if (codbarras <= 9789871989852) {
                return(list(prediction=0, error=0.04286))
            }
        }
    }
    return(NA)
}
