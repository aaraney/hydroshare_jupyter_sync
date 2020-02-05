// potato (vicky): can we add a header comment to this file, esp if it is a 3rd party library we should prob credit them somewhere
// potato (emily): we need to add comments and headers to all of these functions

// potato (emily): overall comment for frontend, we need to reevaluate our prop variables bc sometimes I think we may overcomplicate things
// or be redundant. Maybe not, but I remember being in just "get it working mode" and not really trying to make it pretty
import * as React from 'react';

import {
  AllActionTypes,
  IFileOrFolder,
  SortByOptions,
} from '../store/types';
import '../styles/css/FileList.css';

import {
  Button
} from 'react-bootstrap';

import OpenFileModal from './OpenFileModal';

import { FaFileMedical, FaRegFolder} from "react-icons/fa";

import MaterialTable, {MTableToolbar} from 'material-table';

const HUMAN_READABLE_FILE_SIZES = [
  'B',
  'KB',
  'MB',
  'GB',
  'TB',
  'YB',
];

// potato (emily): Really minor, we should be consistent with , or not
interface IPropsInterface {
  allSelected: boolean
  files: IFileOrFolder[]
  onFileOrFolderSelected: (arg0: IFileOrFolder, arg1: boolean) => AllActionTypes
  selectedFilesAndFolders: Set<string>
  sortBy: SortByOptions | undefined,
  searchTerm: string
  toggleAllSelected: () => AllActionTypes
  hydroShare: boolean,
}

interface IFlatFile {
  name: string,
  size: string,
  type: string,
  dirPath: string,
  id: string,
  parentId?: string,
}

interface IStateInterface {
  showModal: boolean
}

export default class FileList extends React.Component<IPropsInterface, IStateInterface> {

  constructor(props: IPropsInterface) {
    super(props)
    this.state = {
      showModal: false
    };
    this.handleOpenModal = this.handleOpenModal.bind(this);
    this.handleCloseModal = this.handleCloseModal.bind(this);
  }

  public flattenFiles(files: IFileOrFolder[], parentID='', level=0, override=false): [IFlatFile[], boolean] {
    let flatFiles: IFlatFile[] = [];
    // potato (emily): more descriptive name than id
    let id = 1;
    let relevantFileForSearch = false

    files.forEach(fileOrFolder => {
      let subElements;
      let subFileForSearch;
      const idString = parentID === '' ? id.toString(): parentID + '-' + id.toString()
      if (fileOrFolder.contents) {
        const returnValue = this.flattenFiles(fileOrFolder.contents, idString, level+1)
        subElements = returnValue[0]
        subFileForSearch = returnValue[1]
      }
      const searchTermPresent = fileOrFolder.name.toLowerCase().includes(this.props.searchTerm.toLowerCase())
      if (searchTermPresent || subFileForSearch || override) {
        // potato (charlie): not really sure what's up here, but at this point it doesn't seem like a switch 
        // statment is necessary. Don't know if that even matters though.
        // potato (emily): it will be necessary when we have different kinds of file types. this only matters if we keep the 
        // very important emojis
        let fileIcon;
        switch(fileOrFolder.type) {
          case 'folder':
            fileIcon = '📁' // potato (charlie): OMG you can just put icons in code like this?
            break;
          // case 'csv':
          default:
            fileIcon = '📄'
            break;
          // case 'ipynb':
          //   fileIcon = '💻'
          //   break;
          // default:
          //   break;
        }
        relevantFileForSearch = true
        const spacers = this.generateSpaces(level);
        flatFiles.push({
          name: spacers+(fileIcon ? fileIcon : '')+'  ' +fileOrFolder.name,
          size: this.getFormattedSizeString(fileOrFolder.sizeBytes),
          type: fileOrFolder.type,
          dirPath: fileOrFolder.dirPath,
          id: idString,
          parentId: parentID !== '' ? parentID : undefined,
        })
        if (fileOrFolder.contents) {
          if (searchTermPresent || override) {
            flatFiles = flatFiles.concat(this.flattenFiles(fileOrFolder.contents, idString, level+1, true)[0]);
          } else if (subFileForSearch && subElements) {
            flatFiles = flatFiles.concat(subElements)
          }
        }
      }
      id++;
    });
    return [flatFiles, relevantFileForSearch];
  }

  public handleOpenModal () {
    this.setState({ showModal: true });
  }

  public handleCloseModal () {
    this.setState({ showModal: false });
  }

  public render() {
    const { files } = this.props;
    if (!files) {
      return null;
    }

    console.log(this.props.files)

    return (
      <div className='FileList'>
        <MaterialTable
          title={this.props.hydroShare ? "HydroShare files" : "JupyterHub files"}
          columns={[
            { title: 'Name', field: 'name', cellStyle:{ whiteSpace: 'pre'} },
            { title: 'Type', field: 'type' },
            { title: 'Size', field: 'size', type: 'numeric' },
          ]}
          data={this.flattenFiles(this.props.files)[0]}
          parentChildData={(row, rows) => rows.find(a => a.id === row.parentId)}
          options={{
            selection: true,
            sorting: true,
            search: false,
            maxBodyHeight: 500,
            headerStyle: {backgroundColor: '#ededed', fontSize: 16},
            searchFieldStyle: {color: '#ffffff'},
            paging: false,
          }}
          onRowClick={((evt, selectedRow) => this.setState( {showModal: true} ))}
          components={{
            Toolbar: props => (
              <div className="Toolbar">
                <MTableToolbar className="MTtoolbar" {...props} />
                {!this.props.hydroShare && <Button className="new-resource-button" variant="light" onClick={this.handleOpenModal}><FaFileMedical/> New File</Button>}
                {!this.props.hydroShare && <Button className="new-resource-button" variant="light" onClick={this.handleOpenModal}><FaRegFolder/> New Folder</Button>}
              </div>
            )}}
        />
        <OpenFileModal
                show={this.state.showModal}
                onHide={this.handleCloseModal}
              />
      </div>
    )
  }

  private generateSpaces = (count: number): string => {
    let elems ='';
    for (let i = 0; i < count; ++i) {
      elems += '         ';
    }
    return elems;
  };

  // TODO: Write some unit tests
  private getFormattedSizeString = (sizeBytes: number): string => {
    const logSizeBase10Point24 = Math.log(sizeBytes)/Math.log(10.24);
    const labelIndex = Math.floor(logSizeBase10Point24 / 3);
    const sizeInHumanReadableUnits = Math.round(sizeBytes / Math.pow(10.24, labelIndex * 3));
    return `${sizeInHumanReadableUnits}${HUMAN_READABLE_FILE_SIZES[labelIndex]}`;
  };

}
