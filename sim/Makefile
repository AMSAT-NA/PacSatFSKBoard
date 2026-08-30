
doc: Calculating_L_Match.pdf CalculatingPiFilter.pdf directional_coupler.pdf

%.svg: %.dia
	dia --export=$@ $<

%.pdf: %.ltx
	pdflatex -shell-escape $<
	pdflatex -shell-escape $<

Calculating_L_Match.pdf: Calculating_L_Match.ltx LMatch1.svg LMatch2.svg

CalculatingPiFilter.pdf: CalculatingPiFilter.ltx PiFilter.svg \
		InputFilter.svg PAOutInductor.svg

directional_coupler.pdf: directional_coupler.ltx

clean:
	rm -f Calculating_L_Match.aux Calculating_L_Match.log Calculating_L_Match.pdf
	rm -f CalculatingPiFilter.aux CalculatingPiFilter.log CalculatingPiFilter.pdf
	rm -f LMatch1.svg LMatch2.svg PiFilter.svg InputFilter.svg PAOutInductor.svg
	rm -f directional_coupler.pdf directional_coupler.log directional_coupler.aux
	rm -rf svg-inkscape
