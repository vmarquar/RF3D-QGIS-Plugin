library(ggplot2)
library(reshape2)
library("optparse")

print("start R session form py")

option_list = list(
  make_option(c("-f", "--file"), type="character", default="~/Desktop", 
              help="dataset file name", metavar="character")
); 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);
if (is.null(opt$file)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file)", call=FALSE)
}

print(opt$file)


#### MAIN
outpath = dirname(opt$file) # gets the same directory as the csv file
profile_data <- read.csv(opt$file, header = T)

profile_data_oXY = profile_data[-2:-3] # remove X and Y (we dont want to plot them)

profile_data_oXY <- melt(profile_data_oXY, id.vars="Length")

# Everything on the same plot
p1 <- ggplot(profile_data_oXY, aes(Length,value, col=variable)) + 
  geom_point() + 
  stat_smooth() 

# Separate plots
p2 <- ggplot(profile_data_oXY, aes(Length,value)) + 
  geom_line() + 
  #stat_smooth() +
  facet_wrap(variable ~ .,ncol=5,scales = "free_y")

p3 <- ggplot(profile_data_oXY, aes(Length,value)) + 
  geom_line() + 
  ylim(0,10) +
  #stat_smooth() +
  facet_wrap(variable ~ .,ncol=5)
  
# a3 297 x 420
ggsave(filename="Plot1.pdf", plot = p1, device = "pdf", path = outpath, scale = 1, width = 297, height = 420, units=c("mm"), dpi = 300)
ggsave(filename="Plot2-5col.pdf", plot = p2, device = "pdf", path = outpath, scale = 1, width = 297, height = 420, units=c("mm"), dpi = 300)
ggsave(filename="Plot2-5col-10mYlim.pdf", plot = p3, device = "pdf", path = outpath, scale = 1, width = 297, height = 420, units=c("mm"), dpi = 300)

