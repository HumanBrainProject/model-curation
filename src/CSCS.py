from hbp_archive import Container, PublicContainer, Project, Archive


if __name__ == '__main__':
    
    import argparse
    parser=argparse.ArgumentParser()

    # parser.add_argument("Protocol",
    #                     help="""
    #                     type of database update to be applied, choose between:
    #                     - 'Catalog-to-Local' 
    #                     - 'Catalog-to-Local-full-rewriting' (to restart from the CatalogDB)
    #                     - 'Add-KG-Metadata-to-Local'
    #                     - 'Local-to-Spreadsheet' 
    #                     - 'Local'
    #                     - 'Local-to-KG'
    #                     - 'KG-to-Local'
    #                     - 'Release-Summary'
    #                     """)
    parser.add_argument('-c', "--container_name", type=str, help="key to be updated")
    parser.add_argument('-u', "--user", type=str, default='yann')
    parser.add_argument("--url", type=str,
                        default="https://object.cscs.ch/v1/AUTH_6ebec77683fb472f94d352be92b5a577/SNN%20modeling%20in%20vitro%20SWA")
    args = parser.parse_args()

    # if args.container_name=='':
    #     args.container_name = input('name of the CSCS container: ')
    # if args.user=='':
    #     args.user = input('CSCS username: ')

    container = PublicContainer(args.url)
    files = container.list()
    for f in files:
        print('- ', f)

    # Working with a private container
    # container = Container("MyContainer", username="xyzabc") # you will be prompted for your password
    # files = container.list()
    # local_file = container.download("README.txt", overwrite=True) # default is not to overwrite existing files
    # print(container.read("README.txt"))
    # number_of_files = container.count()
    # size_in_MB = container.size("MB")

