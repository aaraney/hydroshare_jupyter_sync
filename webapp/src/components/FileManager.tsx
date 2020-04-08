/**
 * This is a test of the react-beautiful-dnd package. It should be restructured significantly if it is to be used.
 * Tutorial illustrating how to customize appearing during a drag:
 * https://egghead.io/lessons/react-customise-the-appearance-of-an-app-during-a-drag-using-react-beautiful-dnd-snapshot-values
 */

// SPIFFY (Emily) Again, frontend overall needs more commenting I think, especially bc HS devs
// don't know anything about React
import * as React from 'react';
import { ChangeEvent } from 'react';
import {
  DragDropContext,
  DropResult,
} from 'react-beautiful-dnd';

import '../styles/FileManager.scss';

import {
  FileOrFolderTypes,
  IFile,
  IFolder,
} from '../store/types';

import FilePane from './FilePane';

interface IFileManagerState {
  filterByName: string
  selectedLocalFilesAndFolders: Set<string>
  selectedHydroShareFilesAndFolders: Set<string>
}

interface IFileManagerProps {
  hydroShareResourceRootDir: IFolder
  jupyterHubResourceRootDir: IFolder
  copyFileOrFolder: (src: IFile, dest: IFolder) => any
  moveFileOrFolder: (src: IFile, dest: IFolder) => any
  openFile: (file: IFile) => any
  promptCreateNewFileOrFolder: () => any
  promptDeleteFilesOrFolders: (paths: string[]) => any
  resourceId: string
}

// For converting file paths back into IFiles and IFolders
let fileOrFolderLookupTable = new Map<string, IFile | IFolder>();

export default class FileManager extends React.Component<IFileManagerProps, IFileManagerState> {

  state = {
    allHydroShareFilesAndFoldersSelected: false,
    allLocalFilesAndFoldersSelected: false,
    filterByName: '',
    selectedLocalFilesAndFolders: new Set<string>(),
    selectedHydroShareFilesAndFolders: new Set<string>(),
  };

  onDragEnd = (result: DropResult) => {
    const {
      draggableId: srcURI,
      destination: dest,
    } = result;
    if (!dest?.droppableId) {
      // Not sure when this happens, but droppableId is apparently optional
      return;
    }
    const destURI = dest.droppableId;
    const srcFileOrFolder = fileOrFolderLookupTable.get(srcURI) as IFile | IFolder;
    const destFolder = fileOrFolderLookupTable.get(destURI) as IFolder;
    const srcPrefix = srcURI.split(':')[0];
    const destPrefix = destURI.split(':')[0];
    console.log(`Received request to move ${srcURI} to ${destURI}.`);
    const srcParentFolderPathComponents = srcFileOrFolder.path.split('/');
    srcParentFolderPathComponents.pop();
    let srcParentFolderPath = srcParentFolderPathComponents.join('/');
    if (srcParentFolderPathComponents.length === 1) { // Length is 1 if parent folder is root dir
      srcParentFolderPath += '/';
    }
    if (srcParentFolderPath === destFolder.path) {
      console.log("File dropped in same location. Ignoring move request.");
      return;
    }
    if (srcPrefix === destPrefix) {
      // Move files within HydroShare or the local filesystem
      this.props.moveFileOrFolder(srcFileOrFolder, destFolder);
    } else {
      // Copy files between HydroShare and the local filesystem
      this.props.copyFileOrFolder(srcFileOrFolder, destFolder);
    }
    console.log(srcFileOrFolder);
    console.log(destFolder);
  };

  filterByNameChanged = (e: ChangeEvent<HTMLInputElement>) => this.setState({filterByName: e.target.value});

  buildLookupTable = () => {
    fileOrFolderLookupTable.clear();

    if (this.props.jupyterHubResourceRootDir) {
      fileOrFolderLookupTable.set(this.props.jupyterHubResourceRootDir.path, this.props.jupyterHubResourceRootDir);
      this.addFolderContentsToLookupTable(this.props.jupyterHubResourceRootDir);
    }
    if (this.props.hydroShareResourceRootDir) {
      fileOrFolderLookupTable.set(this.props.hydroShareResourceRootDir.path, this.props.hydroShareResourceRootDir);
      this.addFolderContentsToLookupTable(this.props.hydroShareResourceRootDir);
    }
  };

  addFolderContentsToLookupTable = (folder: IFolder) => {
    folder.contents.forEach(item => {
      fileOrFolderLookupTable.set(item.path, item);
      if (item.type === FileOrFolderTypes.FOLDER) {
        this.addFolderContentsToLookupTable(item as IFolder);
      }
    });
  };

  setSelectedHydroShareFilesAndFolders = (items: Set<string>) => this.setState({selectedHydroShareFilesAndFolders: items});
  setSelectedLocalFilesAndFolders = (items: Set<string>) => this.setState({selectedLocalFilesAndFolders: items});

  promptDeleteSelectedHydroShareFiles = () =>
    this.props.promptDeleteFilesOrFolders(Array.from(this.state.selectedHydroShareFilesAndFolders));

  promptDeleteSelectedLocalFiles = () =>
    this.props.promptDeleteFilesOrFolders(Array.from(this.state.selectedLocalFilesAndFolders));

  render() {
    const {
      hydroShareResourceRootDir,
      jupyterHubResourceRootDir,
      openFile,
    } = this.props;

    const {
      filterByName,
    } = this.state;

    // Rebuild the lookup table
    this.buildLookupTable();

    let jupyterHubFilePane;
    if (jupyterHubResourceRootDir) {
      const header =
        <div>
          <div className="title-row">
            <span className="title">JupyterHub Files</span>
            <img src="/JupyterHub-logo.png" alt="JupyterHub logo"/>
          </div>
          <div className="actions-row">
            <input
              className="search"
              onChange={this.filterByNameChanged}
              placeholder="Filter"
              type="text"
              value={filterByName}
            />
            <button onClick={this.props.promptCreateNewFileOrFolder}>New</button>
            <button>Upload</button>
            <button
              onClick={this.promptDeleteSelectedLocalFiles}
              disabled={this.state.selectedLocalFilesAndFolders.size === 0}>
              Delete
            </button>
          </div>
        </div>;
      jupyterHubFilePane =
        <FilePane
          className="tile jupyterhub"
          droppableId={jupyterHubResourceRootDir.path}
          filterByName={filterByName}
          rootDir={jupyterHubResourceRootDir}
          header={header}
          openFile={openFile}
          onSelectedFilesAndFoldersChange={this.setSelectedLocalFilesAndFolders}
        />;
    }
    let hydroShareFilePane;
    if (hydroShareResourceRootDir) {
      const openInHydroShare = () => window.open(`https://www.hydroshare.org/resource/${this.props.resourceId}/`, '_blank');
      const header =
        <div>
          <div className="title-row">
            <span className="title">HydroShare Files</span>
            <img src="/HydroShare-logo.png" alt="HydroShare logo"/>
          </div>
          <div className="actions-row">
            <input
              className="search"
              onChange={this.filterByNameChanged}
              placeholder="Filter"
              type="text"
              value={filterByName}
            />
            <button
              disabled={this.state.selectedHydroShareFilesAndFolders.size === 0}
              onClick={this.promptDeleteSelectedHydroShareFiles}>
              Delete
            </button>
          <button
            onClick={openInHydroShare}
            title="Open the page for this resource in HydroShare">
            Open in HydroShare
          </button>
          </div>
        </div>;
      hydroShareFilePane =
        <FilePane
          className="tile hydroshare"
          droppableId={hydroShareResourceRootDir.path}
          filterByName={filterByName}
          rootDir={hydroShareResourceRootDir}
          header={header}
          onSelectedFilesAndFoldersChange={this.setSelectedHydroShareFilesAndFolders}
        />;
    }

    return (
      <DragDropContext onDragEnd={this.onDragEnd}>
        <div className="FileManager content-row">
          {jupyterHubFilePane}
          {hydroShareFilePane}
        </div>
      </DragDropContext>
    );
  };
}
