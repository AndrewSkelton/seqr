/* eslint-disable no-underscore-dangle */
/* eslint-disable react/no-array-index-key */

import React from 'react'
import PropTypes from 'prop-types'

import { Button, Confirm, Form, Message } from 'semantic-ui-react'
import isEqual from 'lodash/isEqual'

import { HttpRequestHelper } from '../../utils/httpRequestHelper'
import Modal from './Modal'
import { HorizontalSpacer } from '../Spacers'
import SaveStatus from '../form/SaveStatus'


/**
 * Modal dialog that contains form elements.
 *
 * TODO: this component needs to be refactored. It was created based on an older version of
 * SemanticUI.
 */
class ModalWithForm extends React.Component
{
  static propTypes = {
    title: PropTypes.string.isRequired,
    submitButtonText: PropTypes.string,
    formSubmitUrl: PropTypes.string,
    onValidate: PropTypes.func,
    onSave: PropTypes.func,
    onClose: PropTypes.func,
    confirmCloseIfNotSaved: PropTypes.bool.isRequired,
    children: PropTypes.node,
    getFormDataJson: PropTypes.func,  // required if either onValidate or formSubmitUrl is provided
  }

  constructor(props) {
    super(props)

    this.state = {
      saveStatus: SaveStatus.NONE,
      saveErrorMessage: null,
      confirmClose: false,
      errors: {},
      warnings: {},
      info: {},
    }
  }

  componentWillReceiveProps() {
    if (this.props.onValidate) {
      const formData = this.props.getFormDataJson()
      const validationResult = this.props.onValidate(formData)
      this.setState(validationResult)
    }
  }

  formHasBeenModified = () => {
    return !isEqual(this.originalFormData, this.props.getFormDataJson())
  }

  handleSave = (e) => {
    e.preventDefault()

    let validationResult = null
    if (this.props.onValidate) {
      validationResult = this.props.onValidate(this.props.getFormDataJson())
      this.setState(validationResult)

      if (validationResult && validationResult.errors && Object.keys(validationResult.errors).length > 0) {
        return  // don't submit the form if there are errors
      }
    }

    this.setState({ saveStatus: SaveStatus.IN_PROGRESS, saveErrorMessage: null })

    const formSubmitUrl = (validationResult && validationResult.formSubmitUrl) || this.props.formSubmitUrl
    if (formSubmitUrl) {
      const httpRequestHelper = new HttpRequestHelper(
        formSubmitUrl,
        (responseJson) => {
          if (this.props.onSave) {
            this.props.onSave(responseJson)
          }
          this.handleClose()
        },
        (exception) => {
          console.log(exception)
          this.setState({
            saveStatus: SaveStatus.ERROR,
            saveErrorMessage: exception.message.toString(),
          })
        },
      )

      httpRequestHelper.post({ form: this.props.getFormDataJson() })
    } else {
      this.handleClose(false)
    }
  }

  handleClose = (confirmCloseIfNecessary) => {
    if (confirmCloseIfNecessary && this.props.confirmCloseIfNotSaved && this.formHasBeenModified()) {
      //first double check that user wants to close
      this.setState({ confirmClose: true })
    } else if (this.props.onClose) {
      this.props.onClose()
    }
  }

  renderForm() {
    const children = React.Children.map(
      this.props.children,
      child => (
        child.props && child.props.name && this.state.errors && this.state.errors[child.props.name] !== undefined ?
          React.cloneElement(child, { error: true }) : child
      ),
    )

    const formComponent = (
      <Form onSubmit={this.handleSave} style={{ textAlign: 'left' }}>
        {children}
      </Form>
    )

    return formComponent
  }

  renderMessageBoxes() {
    return <span style={{ textAlign: 'left' }}>
      {
        (Object.keys(this.state.info).length > 0) &&
        <Message info style={{ marginTop: '10px' }}>
          {Object.values(this.state.info).map((info, i) => <div key={i}>{info}<br /></div>)}
        </Message>
      }
      {
        (Object.keys(this.state.warnings).length > 0) &&
        <Message warning style={{ marginTop: '10px' }}>
          {Object.values(this.state.warnings).map((warning, i) => <div key={i}><b>WARNING:</b> {warning}<br /></div>)}
        </Message>
      }
      {
        (Object.keys(this.state.errors).length > 0) &&
        <Message error style={{ marginTop: '10px' }}>
          {Object.values(this.state.errors).map((error, i) => <div key={i}><b>ERROR:</b> {error}<br /></div>)}
        </Message>
      }
    </span>
  }

  renderButtonPanel() {
    return <div style={{ margin: '15px 0px 15px 10px', width: '100%', textAlign: 'right' }}>
      <Button
        onClick={(e) => { e.preventDefault(); this.handleClose(true) }}
        style={{ padding: '5px', width: '100px' }}
      >
        Cancel
      </Button>
      <HorizontalSpacer width={10} />
      <Button
        onClick={this.handleSave}
        type="submit"
        color="vk"
        style={{ padding: '5px', width: '100px' }}
      >
        {this.props.submitButtonText || 'Submit'}
      </Button>
      <HorizontalSpacer width={5} />
      <SaveStatus status={this.state.saveStatus} errorMessage={this.state.saveErrorMessage} />
      <HorizontalSpacer width={5} />
    </div>
  }

  renderConfirmCloseDialog() {
    return <Confirm
      content="Editor contains unsaved changes. Are you sure you want to close it?"
      open={this.state.confirmClose}
      onCancel={() => this.setState({ confirmClose: false })}
      onConfirm={() => this.handleClose(false)}
    />
  }

  render() {
    return <Modal title={this.props.title} onClose={() => this.handleClose(true)}>
      <div>
        {this.renderForm()}
        {this.renderMessageBoxes()}
        {this.renderButtonPanel()}
        {this.renderConfirmCloseDialog()}
      </div>
    </Modal>
  }

}


export default ModalWithForm
