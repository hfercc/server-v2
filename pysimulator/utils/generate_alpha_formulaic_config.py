from xml.etree.ElementTree import ElementTree,Element
from optparse import OptionParser
import os
 
def read_xml(in_path):
    tree = ElementTree()
    tree.parse(in_path)
    return tree
 
def write_xml(tree, out_path):
    tree.write(out_path)
 
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--alpha_id',dest='alpha_id')
    parser.add_option('--formula', dest='formula')
    parser.add_option('--output_dir', dest='output_dir', default='.')
    parser.add_option('--templates', dest='templates', default='utils/config_templates')
    (options, args) = parser.parse_args()

    if os.path.exists(options.output_dir) == False:
        os.makedirs(options.output_dir)

    formula_path = os.path.join(options.output_dir, 'formula.txt')
    formula_f = open(formula_path, 'w')
    formula_f.write(options.formula)
    formula_f.close()

    configs = os.listdir(options.templates)
    for cfg in configs:
        read_path = options.templates + '/' + cfg
        cfg_name = cfg.replace('ALPHAID', options.alpha_id)
        name = cfg_name.split('.')[0]

        target_foldor = options.output_dir + '/config' 
        if os.path.exists(target_foldor) == False:
            os.makedirs(target_foldor)

        write_path = target_foldor + '/' + cfg_name

        tree = read_xml(read_path)
        root = tree.getroot()

        alpha_node = root.find('Alpha')
        alpha_node.set('id', options.alpha_id)
        alpha_node.set('formula', options.formula)

        prf_node = root.find('Performance')
        prf_node.set('save_dir', './output/{0}'.format(options.alpha_id))
        prf_node.set('output_name', name)

        write_xml(tree, write_path)
