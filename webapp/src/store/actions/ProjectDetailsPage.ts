import { action } from 'typesafe-actions';
import {
  ProjectDetailsPageActions,
} from './action-names';
import {
    getResourceLocalFiles,
    getResourceHydroShareFiles,
} from '../async-actions';
import {
    IFileOrFolder,
    IJupyterProject,
    IRootState,
    SortByOptions,
} from '../types';
import { AnyAction } from 'redux';
import {
    ThunkAction,
    ThunkDispatch,
} from "redux-thunk";

export function getFilesIfNeeded(project: IJupyterProject): ThunkAction<Promise<void>, {}, {}, AnyAction> {
    return async (dispatch: ThunkDispatch<{}, {}, AnyAction>) => {
        if (project && !project.files) {
            dispatch(getResourceLocalFiles(project.id));
        }
        if (project && project.hydroShareResource && !project.hydroShareResource.files) {
            dispatch(getResourceHydroShareFiles(project.id));
        }
    };
}

export function openFileInJupyterHub(project: IJupyterProject, file: IFileOrFolder) {
    return async (dispatch: ThunkDispatch<{}, {}, AnyAction>, getState: () => IRootState) => {
        const state = getState();
        if (state.user) {
            const userName = state.user.username;
            const projectId = project.id;
            const filePath = `${file.name}.${file.type}`;
            const url = `https://jupyter.cuahsi.org/user/${userName}/notebooks/notebooks/data/${projectId}/${projectId}/data/contents/${filePath}`;
            window.open(url, '_blank');
        }
    };
}

export function toggleIsSelectedAllLocal(project: IJupyterProject) {
    return action(ProjectDetailsPageActions.TOGGLE_IS_SELECTED_ALL_JUPYTER, project);
}

export function toggleIsSelectedAllHydroShare(project: IJupyterProject) {
    return action(ProjectDetailsPageActions.TOGGLE_IS_SELECTED_ALL_HYDROSHARE, project);
}

export function toggleIsSelectedOneLocal(fileOrFolder: IFileOrFolder) {
    return action(ProjectDetailsPageActions.TOGGLE_IS_SELECTED_ONE_JUPYTER, fileOrFolder);
}

export function toggleIsSelectedOneHydroShare(fileOrFolder: IFileOrFolder) {
    return action(ProjectDetailsPageActions.TOGGLE_IS_SELECTED_ONE_HYDROSHARE, fileOrFolder);
}

export function searchProjectBy(searchTerm: string) {
    return action(ProjectDetailsPageActions.SEARCH_PROJECT_BY, searchTerm);
  }

export function sortBy(sortTerm: SortByOptions) {
    return action(ProjectDetailsPageActions.SORT_BY_NAME, sortTerm);
}