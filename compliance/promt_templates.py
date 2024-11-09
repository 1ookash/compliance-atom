from textwrap import dedent

system_promt_template = dedent(
    '''
        Comparison Prompt for HMI and SSTS Documents

        Objective:
        Evaluate the compliance of the HMI document against the SSTS document for the feature "Driver initiate a call through SWP" and provide a final assessment based on the provided table with marks. Your assessment should be based on how much percentage you can perform the function from document HMI  following document SSTS

        table with marks:
        Abbr.	Name 	Explanation	Value
        FC	Fully compliant 	Perfect! Nothing can be improved.	5
        LC	Largely compliant	Generally correct. Some improvement may be needed (described in comments). No need for review.	4
        PC	Partially compliant	Major deviations. Improvements needed (described in comments). After the improvement, review is required.	3
        NC	Non-compliant	Not compliant. Needs to be re-done and re-reviewed. Directions for update shown in comments.	2
        NA	Not applicable	Not applicable. Reason for not-applicability is described in comments.	1

        Documents:

            HMI Document:
                Title: [I-6583] Driver initiate a call through SWP
                Preconditions:
                    The IVI is on.
                    The vehicle can be shifted to any of the PRND drive modes.
                    The driver's smartphone is connected to the vehicle's system via Bluetooth.
                    The driver has granted necessary permissions for phone information.
                Main Scenario:
                    The driver navigates to the 'Calls' option on the SWP Android.
                    The driver initiates a call by selecting a number from the recent calls list.
                    The interior ambient light changes color to signal the outgoing call.
                    The call status is displayed on the HUD and SWP Android.
                    The vehicle's microphone and speakers are used for the call.
                Postconditions:
                    If the call is initiated successfully, the SWP Android displays an active call interface.
                    The driver is able to use the hands-free phone functionality on the SWP Android.
                Alternative Scenarios:
                    A: Voice assistant initiates a call.
                    B: Recent calls list is empty.
                    C: GSM network is not available.

            SSTS Document:
                Title: Make a call (B sample)
                Functional Description:
                    Users can dial through IVI and make phone calls. Only when the vehicle is stopped can calls be made through SWP.
                Enabling Conditions:
                    IVI system startup.
                    User can operate SWP.
                    Mobile Bluetooth connected.
                Trigger Conditions:
                    Toggledialpad via SWP to make a call.
                    Make a call through voice commands.
                    Make a call through the mobile phone.
                    Toggle 'Call' menu option via SWP.
                    Select contact for calling in synchronized phonebook via SWP.
                    Call the roadside assistance hotline.
                Execution Output:
                    Dialpad interface with numeric keyboard and dialing software buttons.
                    Dialing process and call interface.
                    Interrupting number dialing.
                    Activating and switching audio channel to Bluetooth phone.
                    Displaying call status through SWP.
                    Inputting numbers in tone mode during the call.
                    Calling the roadside assistance hotline.
                Exit Conditions:
                    IVI system shutdown.
                    Bluetooth disconnected.
                    User stopped call.
                    The other party hung up the phone.
                Notes:
                    Text prompt for unpaired smartphone.

        Comparison Table:
        Criteria	HMI Document	SSTS Document	Differences	Compliance Level
        Preconditions	The vehicle can be shifted to any of the PRND drive modes.	Only when the vehicle is stopped can calls be made through SWP.	HMI allows calls in any drive mode, while SSTS restricts calls to when the vehicle is stopped.	NC
        Main Scenario	Driver initiates a call by selecting a number from the recent calls list.	Driver can also toggle the dialpad to enter a number directly.	SSTS includes additional functionality for entering numbers directly.	PC
        Alternative Scenarios	Voice assistant initiates a call, recent calls list is empty, GSM network not available.	Includes calling the roadside assistance hotline.	SSTS includes additional functionality for calling the roadside assistance hotline.	PC
        Execution Output	Displays call status on HUD and SWP Android.	Displays call status on SWP and allows inputting numbers in tone mode.	SSTS includes additional functionality for inputting numbers in tone mode.	PC
        Exit Conditions	None specified.	IVI system shutdown, Bluetooth disconnected, user stopped call, other party hung up.	SSTS provides more detailed exit conditions.	PC

        Final Assessment:

            Overall Compliance Level: NC
            Reasoning:
                The primary discrepancy is the restriction on making calls only when the vehicle is stopped in the SSTS document, which is not mentioned in the HMI document. This is a significant safety concern and requires a major deviation.
                While the SSTS document includes additional functionalities and detailed conditions, these do not fully mitigate the non-compliance due to the safety restriction.

        return result is json like that
        {
        "Number":"6583";
        "Name":"Driver initiate a call through SWP";
        "Differences":"SSTS describes that only when the vehicle is stopped can calls be made through SWP.
        HMI requires "The vehicle can be shifted to any of the PRND drive modes."";
        "Description":"Additionally SSTS describes:
        - a numeric keyboard (Toggle dialpad via SWP to make a call, if the driver doesn't have this number in contacts,Enter the phone number on the dialpad to make a call.)
        - displays the hotline number of roadside assistance call.";
        "Complience Level":"NC";
        }
        And json with difference between UC and STSS and grade of it and where did it occur in the text Preconditions, Main Scenario, Postconditions, Alternative Scenario. Category need to be one of this  Preconditions, Main Scenario, Postconditions, Alternative Scenario and NA. Each category can have several items.I need a field with name "Source" in json where more information is found in UC, STSS or both

    '''
)

user_promt_template = dedent(
    '''
    HMI Document:
    {reference}
    SSTS Document:
    {source}
    '''
)
