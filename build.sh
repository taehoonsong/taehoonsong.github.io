#!/usr/bin/env bash

USER_OPT=$1

gen_html(){
    uv run generate_website.py
}

gen_pdf(){

    if [ ! -f "./pages/resume.tex" ]; then 
        echo resume.tex missing... try running 'build.sh html'
        exit 0
    fi

    # Convert resume.tex to pdf using pdflatex
    pdflatex --output-directory=pages ./pages/resume.tex

    # clean up
    cd pages
    latexmk -c
}

main(){

    case $USER_OPT in
        html) gen_html ;;
        pdf) gen_pdf;;
        all) gen_html && gen_pdf ;;
        *) echo valid options are html, pdf, or all ;;
    esac
}

main
