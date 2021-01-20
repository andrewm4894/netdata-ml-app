def process_opts(opts):
    if opts != '':
        try:
            opts = opts.split(',')
            opts = [opt.split('=') for opt in opts]
            opts = {opt[0]: opt[1] for opt in opts}
        except:
            opts = {}
    else:
        opts = {}
    return opts