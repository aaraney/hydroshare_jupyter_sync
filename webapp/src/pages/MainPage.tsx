// TODO (Emily): in general i think adding some more comments to these files would be great -
// at a minimum let's make sure we at least have a header comment for each one just saying what the file does
import * as React from 'react';
import ResourceList from '../components/ResourceList';
import { connect } from 'react-redux';
import { ThunkDispatch } from "redux-thunk";

import * as AppActions from '../store/actions/App';
import {
  createNewResource,
  deleteResources,
} from '../store/async-actions';
import {
  IResource,
  IRootState,
  ICreateResourceRequest,
} from '../store/types';

const mapStateToProps = ({ resources }: IRootState) => {
  return {
    resources: resources.allResources,
    fetchingResources: resources.fetchingResources,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<{}, {}, any>) => {
  return {
    deleteResources: (resources: IResource[]) => dispatch(deleteResources(resources, false)),
    deleteResourcesLocally: (resources: IResource[]) => dispatch(deleteResources(resources, true)),
    viewResource: (resource: IResource) => dispatch(AppActions.viewResource(resource)),
    createResource: (newResource: ICreateResourceRequest) => dispatch(createNewResource(newResource))
  }
};

type ReduxType = ReturnType<typeof mapStateToProps> & ReturnType<typeof mapDispatchToProps>;

class MainPage extends React.Component<ReduxType, never>  {

  public handleViewResource = (resource: IResource) => {
    this.props.viewResource(resource);
  };

  public render() {
    return (
      <div className="page resources">
        <ResourceList
          className="tile"
          deleteResources={this.props.deleteResources}
          deleteResourcesLocally={this.props.deleteResourcesLocally}
          fetchingResources={this.props.fetchingResources}
          createResource={this.props.createResource}
          viewResource={this.handleViewResource}
          resources={this.props.resources}
        />
      </div>
    )
  }

}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MainPage);
