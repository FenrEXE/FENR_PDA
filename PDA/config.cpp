/*
    Fenrir Industries PDA
    DayZ communication and administration system

    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    PBO prefix FENR_PDA\PDA (v8.6): every asset path starts with
    FENR_PDA\PDA\ (work drive folder P:\FENR_PDA\PDA).
*/

class CfgPatches
{
	class FENR_PDA
	{
		units[]=
		{
			"FENR_PDA_IntelDrive",
			"FENR_PDA_EncryptedDrive",
			"FENR_PDA_Device"
		};
		weapons[]={};
		requiredVersion=0.1;
		requiredAddons[]=
		{
			"DZ_Data",
			"DZ_Scripts",
			"JM_CF_Scripts",
			"DZM_VPPAdminToolsScripts"
		};
	};
};
class CfgMods
{
	class FENR_Industries_PDA
	{
		dir="FENR_PDA";
		picture="";
		action="";
		hideName=0;
		hidePicture=1;
		name="Fenrir Industries PDA";
		author="Fenr.EXE";
		credits="Fenrir Industries";
		authorID="";
		version="8.8";
		extra=0;
		type="mod";
		inputs="FENR_PDA/PDA/data/inputs.xml";
		dependencies[]={"Game","World","Mission"};
		class defs
		{
			class gameScriptModule
			{
				value="";
				files[]=
				{
					"FENR_PDA/PDA/scripts/3_Game"
				};
			};
			class worldScriptModule
			{
				value="";
				files[]=
				{
					"FENR_PDA/PDA/scripts/4_World"
				};
			};
			class missionScriptModule
			{
				value="";
				files[]=
				{
					"FENR_PDA/PDA/scripts/5_Mission"
				};
			};
		};
	};
};
class CfgVehicles
{
	class Inventory_Base;
	// Shared base for the PDA drives (not spawnable).  v8.7: the plain flash
	// drive item and its PDA slot were removed; its model stays as the body
	// of the Intel and Encrypted drives.
	class FENR_PDA_DriveBase: Inventory_Base
	{
		scope=0;
		displayName="Data Drive";
		descriptionShort="A Fenrir Industries data drive.";
		model="FENR_PDA\PDA\data\flashdrive.p3d";
		itemSize[]={1,1};
		weight=250;
		class DamageSystem
		{
			class GlobalHealth
			{
				class Health
				{
					hitpoints=50;
					healthLevels[]=
					{
						
						{
							1,
							
							{
								"FENR_PDA\PDA\data\flashdrive.rvmat"
							}
						},
						
						{
							0.69999999,
							
							{
								"FENR_PDA\PDA\data\flashdrive.rvmat"
							}
						},
						
						{
							0.5,
							
							{
								"FENR_PDA\PDA\data\flashdrive_damage.rvmat"
							}
						},
						
						{
							0.30000001,
							
							{
								"FENR_PDA\PDA\data\flashdrive_damage.rvmat"
							}
						},
						
						{
							0,
							
							{
								"FENR_PDA\PDA\data\flashdrive_destruct.rvmat"
							}
						}
					};
				};
			};
		};
	};
	// The two drive types.  Each has its own PDA slot, so a PDA can carry
	// one of each.
	class FENR_PDA_IntelDrive: FENR_PDA_DriveBase
	{
		scope=2;
		title="Intel Drive";
		displayName="Intel Drive";
		descriptionShort="A recovered data drive. Insert it into a PDA to read the files stored on it.";
		inventorySlot[]=
		{
			"FENR_PDAIntelDrive"
		};
	};
	class FENR_PDA_EncryptedDrive: FENR_PDA_DriveBase
	{
		scope=2;
		title="Encrypted Drive";
		displayName="Encrypted Drive";
		descriptionShort="A PIN-protected Fenrir Industries drive. Stores map markers and group records behind a 4 digit PIN.";
		inventorySlot[]=
		{
			"FENR_PDAEncryptedDrive"
		};
	};
	class FENR_PDA_Device: Inventory_Base
	{
		scope=2;
		title="#pda_item_name";
		displayName="#pda_item_name";
		descriptionShort="#pda_item_desc";
		model="FENR_PDA\PDA\data\pda.p3d";
		animClass="ItemPDA";
		itemSize[]={2,2};
		weight=250;
		repairableWithKits[]={5,7};
		repairCosts[]={30,25};
		oldpower=0;
		attachments[]=
		{
			"BatteryD",
			"FENR_PDAIntelDrive",
			"FENR_PDAEncryptedDrive"
		};
		class EnergyManager
		{
			hasIcon=1;
			autoSwitchOff=1;
			energyUsagePerSecond=9.9999997e-005;
			plugType=1;
			attachmentAction=1;
			wetnessExposure=0.1;
		};
		class DamageSystem
		{
			class GlobalHealth
			{
				class Health
				{
					hitpoints=50;
					healthLevels[]=
					{
						
						{
							1,
							
							{
								"FENR_PDA\PDA\data\pda.rvmat"
							}
						},
						
						{
							0.69999999,
							
							{
								"FENR_PDA\PDA\data\pda.rvmat"
							}
						},
						
						{
							0.5,
							
							{
								"FENR_PDA\PDA\data\pda_damage.rvmat"
							}
						},
						
						{
							0.30000001,
							
							{
								"FENR_PDA\PDA\data\pda_damage.rvmat"
							}
						},
						
						{
							0,
							
							{
								"FENR_PDA\PDA\data\pda_destruct.rvmat"
							}
						}
					};
				};
			};
		};
	};
};
class CfgSlots
{
	class Slot_FENR_PDAIntelDrive
	{
		name="FENR_PDAIntelDrive";
		displayName="Intel Drive";
		ghostIcon="default";
	};
	class Slot_FENR_PDAEncryptedDrive
	{
		name="FENR_PDAEncryptedDrive";
		displayName="Encrypted Drive";
		ghostIcon="default";
	};
};
class CfgSoundShaders
{
	class baseCharacter_SoundShader;
	class FENR_PDA_Message_SoundShader: baseCharacter_SoundShader
	{
		samples[]=
		{
			
			{
				"FENR_PDA\PDA\sounds\new_message",
				1
			}
		};
		volume=0.5;
	};
	class FENR_PDA_SOS_SoundShader: baseCharacter_SoundShader
	{
		samples[]=
		{
			
			{
				"FENR_PDA\PDA\sounds\sos_alarm",
				1
			}
		};
		volume=0.9;
	};
};
class CfgSoundSets
{
	class baseCharacter_SoundSet;
	class FENR_PDA_Message_SoundSet: baseCharacter_SoundSet
	{
		soundShaders[]=
		{
			"FENR_PDA_Message_SoundShader"
		};
	};
	class FENR_PDA_SOS_SoundSet: baseCharacter_SoundSet
	{
		soundShaders[]=
		{
			"FENR_PDA_SOS_SoundShader"
		};
	};
};
