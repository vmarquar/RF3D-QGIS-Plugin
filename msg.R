library("optparse")

option_list = list(
  make_option(c("-f", "--file"), type="character", default="/Users/Valentin/Desktop", 
              help="dataset file name", metavar="character")
); 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);
if (is.null(opt$file)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file)", call=FALSE)
}

print(opt$file)
fileConn<-file(opt$file)
writeLines(c("Hello","World"), fileConn)
close(fileConn)
