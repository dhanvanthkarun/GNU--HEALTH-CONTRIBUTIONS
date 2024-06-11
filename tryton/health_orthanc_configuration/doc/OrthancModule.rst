Connection Configuration
========================

This module is used to configure the connection between Orthanc's DICOM servers and GNU Health. The main part of the module is the OrthancServerConfig model. The label of a server is a name that the user can choose to represent the server directly. The domain field contains the full web address (URL) to the Orthanc server. This helps GNU Health to find the correct server to connect to. The user must also provide a username and password to log in to the Orthanc server. 


Configuration
-------------

.. class:: health_orthanc_configuration.OrthancServerConfig(ModelSQL, ModelView)
    
    This class, `OrthancServerConfig`, is used to connect to an Orthanc DICOM server and to check if a connection to the corresponding domain can be established.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief description of each method:

    - ``__setup__(cls)``: Set up the class for database access by initializing properties and contstrains, such as ensuring the uniqueness 
        of the ``label`` and ``domain`` fields.

    - ``quick_check(domain, user, password)``: Checks if the server details are correct by attempting to connect to the Orthanc DICOM server with the provided domain.

    - ``on_change_with_validated(self)``: Updates the validated field based on the current server details by calling the ``quick_check`` method with the ``domain``, ``user``, and ``password`` attributes.


Wizard
------

.. class:: health_orthanc_configuration.wizard.AddOrthancInit(ModelView)
  
  This class definition `AddOrthancInit` is a model view for initializing an Orthanc connection.
    
  :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
  :type ModelView: class: ``trytond.model.ModelView``

  - ``label``: Represents the label of the Orthanc server. Must be unique.

  - ``domain``: Represents the full URL of the Orthanc server.

  - ``user``: Represents the username for the Orthanc REST server.

  - ``password``: Represents the password for the Orthanc REST server.


.. class:: health_orthanc_configuration.wizard.ConnectNewOrthancServer(Wizard)
 
  This class, `ConnectNewOrthancServer` defines a wizard for connecting to an Orthanc server. 

  :param Wizard: A finite state machine. 
  :type Wizard: class: ``trytond.wizard.Wizard``

   Here's what each class method does:

  - ``start``: Displays the initial state of the wizard, asking for the label, URL, username, and password of the Orthanc server.

  - ``connect``: Handles the transition when the 'Begin' button is pressed. It attempts to connect to the Orthanc server using the provided credentials. 

  - ``status``: Displays the status of the connection attempt. It includes a 'Close' button.

  - ``transition_connect()``: Connects to the Orthanc servers, handles different exceptions, logs the success or failure of the connection attempt, and return 'status' after completion. 
 
  - ``default_status(fields)``: Generates a default status dictionary based on the provided fields.






