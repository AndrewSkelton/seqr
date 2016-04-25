import gzip
import sys
from django.core.management.base import BaseCommand
from xbrowse_server.base.models import Project
from xbrowse_server import sample_management
from xbrowse.parsers import vcf_stuff
from xbrowse.utils import slugify
from xbrowse_server.base.management.commands.convert_xls_to_ped import parse_xl_workbook, write_xl_rows_to_ped

try:
    from openpyxl import load_workbook
except ImportError:
    print("WARNING: Couldn't import openpyxl. --xls option will not work")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--sample-list',
                    dest='sample-list',
                    default=False,
                    help='A sample list to gather patient information from.')
        parser.add_argument('--vcf',
                    help='A VCF file to gather patient information from.'
                    )
        parser.add_argument('--ped',
                    help='A PED file to gather patient information from (PREFERRED due to richer information set).'
                    )
        parser.add_argument('--xls',
                    help=('An Excel spreadsheet with the following columns: '
                          'Collaborator Family ID, Collaborator Sample ID, Collaborator Father Sample ID, '
                          'Collaborator Mother Sample ID, Sex, Affected Status. '
                          'For example: ["NR", "NR_0", "NR_1", "NR_2", "Male", "Affected"]')
                    )
        parser.add_argument('args', nargs='*')


    def handle(self, *args, **options):

        if len(args)==0 or options['vcf'] is None and options['ped'] is None and options['xls'] is None:
          print '\n\nPlease enter a VCF file (--vcf), OR IDEALLY A PED or XLS file (using --ped or --xls), and a project ID (first positional argument).'
          print 'For example: python manage.py add_individuals_to_project  myProjectId --ped myPed.ped\n'
          sys.exit()
          
        project_id = args[0]
        project = Project.objects.get(project_id=project_id)

        if options.get('sample_list'):
            indiv_id_list = []
            for line in open(options.get('sample_list')):
                if line.strip() == "" or line.startswith('#'):
                    continue
                indiv_id_list.append(line.strip())
            sample_management.add_indiv_ids_to_project(project, indiv_id_list)

        if options.get('vcf'):
            vcf_path = options.get('vcf')
            if vcf_path.endswith('.gz'):
                vcf = gzip.open(vcf_path)
            else:
                vcf = open(vcf_path)
            indiv_id_list = vcf_stuff.get_ids_from_vcf(vcf)
            sample_management.add_indiv_ids_to_project(project, indiv_id_list)


        if options.get('ped'):
            fam_file = open(options.get('ped'))
            individual_details = sample_management.update_project_from_fam(project, fam_file)
            for j in individual_details:
                print("Adding %s: %s" % (j['indiv_id'], j))

        if options.get('xls'):
            xls_file = options.get('xls')
            title_row, xl_rows = parse_xl_workbook(xls_file)

            temp_ped_filename = 'temp.ped'
            write_xl_rows_to_ped(temp_ped_filename, xl_rows)
            individual_details = sample_management.update_project_from_fam(project, open(temp_ped_filename))
            
            #for j in individual_details:
            #    print("Adding %s: %s" % (j['indiv_id'], j))
                   
