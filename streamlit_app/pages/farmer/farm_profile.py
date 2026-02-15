"""Farm Profile - Manage farm information and profile settings."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_farmer_data():
    """Get farmer data from API."""
    return make_api_request("GET", "/api/farmer/admin")

def update_farmer_data(farmer_data):
    """Update farmer data via API."""
    farmer = get_farmer_data()
    if farmer:
        return make_api_request("PUT", f"/api/farmer/{farmer['id']}", farmer_data)
    return None

def show_farm_profile():
    """Display farm profile management interface."""
    st.title("🏡 Farm Profile")
    st.markdown("### Manage your farm information and settings")
    st.markdown("---")

    # Tabs for different profile sections
    tab1, tab2 = st.tabs(["Farm Details", "Contact Information"])

    with tab1:
        show_farm_details()

    with tab2:
        show_contact_information()

def show_farm_details():
    """Display farm details form."""
    st.subheader("🌾 Farm Details")

    # Load existing farmer data
    try:
        farmer = get_farmer_data()
        if not farmer:
            st.warning("Unable to load farmer data. Please check your connection.")
            farmer = {}
    except Exception as e:
        st.error(f"Error loading farmer data: {str(e)}")
        farmer = {}

    with st.form("farm_details_form"):
        col1, col2 = st.columns(2)

        with col1:
            farm_name = st.text_input(
                "Farm Name *",
                value=farmer.get('farm_name', ''),
                placeholder="e.g., Green Valley Farm",
                help="The name of your farm as it will appear to customers"
            )

            farmer_name = st.text_input(
                "Farmer Name *",
                value=farmer.get('name', ''),
                placeholder="e.g., John Smith",
                help="Your name as the farm owner/operator"
            )

            farm_type = st.selectbox(
                "Farm Type",
                ["Organic", "Conventional", "Hydroponic", "Mixed", "Specialty"],
                index=0,  # Default to Organic for now
                help="Select the type of farming you practice"
            )

        with col2:
            # Combine city and country for location display
            current_location = f"{farmer.get('city', '')}, {farmer.get('country', '')}" if farmer.get('city') else ""
            location = st.text_input(
                "Farm Location *",
                value=current_location,
                placeholder="e.g., Springfield, IL",
                help="City and state where your farm is located"
            )

            farm_size = st.number_input(
                "Farm Size (acres)",
                min_value=0.1,
                max_value=10000.0,
                value=10.0,  # Default value since this isn't in the basic farmer model
                step=0.5,
                help="Total acreage of your farm"
            )

            established_year = st.number_input(
                "Year Established",
                min_value=1800,
                max_value=2024,
                value=2010,  # Default value
                help="Year your farm was established"
            )

        description = st.text_area(
            "Farm Description",
            value="",  # This would come from farmer_profile if we had it
            placeholder="Tell customers about your farm, farming practices, and what makes your products special...",
            height=100,
            help="This description will be visible to customers browsing your products"
        )

        certifications = st.multiselect(
            "Certifications",
            ["USDA Organic", "Non-GMO Project", "Fair Trade", "Rainforest Alliance", "Local Grown"],
            default=[],  # This would come from farmer_profile if we had it
            help="Select any certifications your farm has received"
        )

        submitted = st.form_submit_button("💾 Save Farm Details", type="primary")

        if submitted:
            if farm_name and farmer_name and location:
                try:
                    # Parse location into city and country
                    location_parts = location.split(',')
                    city = location_parts[0].strip() if len(location_parts) > 0 else ""
                    country = location_parts[1].strip() if len(location_parts) > 1 else "Israel"

                    # Prepare farmer data update
                    farmer_update = {
                        'name': farmer_name,
                        'farm_name': farm_name,
                        'city': city,
                        'country': country
                    }

                    # Update farmer data
                    result = update_farmer_data(farmer_update)
                    if result:
                        st.success("✅ Farm details saved successfully!")
                        st.rerun()  # Refresh to show updated data
                    else:
                        st.error("❌ Failed to save farm details. Please try again.")

                except Exception as e:
                    st.error(f"❌ Error saving farm details: {str(e)}")
            else:
                st.error("❌ Please fill in all required fields marked with *")

def show_contact_information():
    """Display contact information form."""
    st.subheader("📞 Contact Information")

    # Load existing farmer data
    try:
        farmer = get_farmer_data()
        if not farmer:
            st.warning("Unable to load farmer data. Please check your connection.")
            farmer = {}
    except Exception as e:
        st.error(f"Error loading farmer data: {str(e)}")
        farmer = {}

    with st.form("contact_info_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "Email Address *",
                value=farmer.get('email', ''),
                placeholder="farmer@example.com",
                help="Primary email for customer communications"
            )

            phone = st.text_input(
                "Phone Number",
                value=farmer.get('phone', ''),
                placeholder="(555) 123-4567",
                help="Phone number for customer inquiries"
            )

            website = st.text_input(
                "Website (optional)",
                value="",  # This would come from farmer_profile if we had it
                placeholder="https://www.yourfarm.com",
                help="Your farm's website if you have one"
            )

        with col2:
            # Combine address fields for display
            address_parts = []
            if farmer.get('address_line1'):
                address_parts.append(farmer['address_line1'])
            if farmer.get('address_line2'):
                address_parts.append(farmer['address_line2'])
            if farmer.get('city'):
                city_line = farmer['city']
                if farmer.get('postal_code'):
                    city_line += f" {farmer['postal_code']}"
                address_parts.append(city_line)
            if farmer.get('country') and farmer['country'] != 'Israel':
                address_parts.append(farmer['country'])

            address = st.text_area(
                "Farm Address",
                value='\n'.join(address_parts) if address_parts else '',
                placeholder="123 Farm Road\nSpringfield, IL 62701",
                height=80,
                help="Physical address of your farm"
            )

            business_hours = st.text_area(
                "Business Hours",
                value="",  # This would come from farmer_profile if we had it
                placeholder="Monday-Friday: 8AM-5PM\nSaturday: 9AM-3PM\nSunday: Closed",
                height=80,
                help="When customers can contact you or visit"
            )

        # Social Media Links
        st.markdown("**Social Media (optional)**")
        col1, col2, col3 = st.columns(3)

        with col1:
            facebook = st.text_input("Facebook", value="", placeholder="https://facebook.com/yourfarm")

        with col2:
            instagram = st.text_input("Instagram", value="", placeholder="@yourfarm")

        with col3:
            twitter = st.text_input("Twitter", value="", placeholder="@yourfarm")

        submitted = st.form_submit_button("💾 Save Contact Information", type="primary")

        if submitted:
            if email:
                try:
                    # Parse address back into components
                    address_lines = address.strip().split('\n')
                    address_line1 = address_lines[0] if len(address_lines) > 0 else ""
                    address_line2 = address_lines[1] if len(address_lines) > 1 else ""

                    # Simple parsing - you might want more sophisticated parsing
                    city_postal = address_lines[-2] if len(address_lines) > 2 else address_lines[-1] if len(address_lines) > 0 else ""
                    city = city_postal.split()[0] if city_postal else ""
                    postal_code = city_postal.split()[-1] if len(city_postal.split()) > 1 else ""

                    # Prepare contact info update
                    contact_update = {
                        'email': email,
                        'phone': phone,
                        'address_line1': address_line1,
                        'address_line2': address_line2 if address_line2 else None,
                        'city': city,
                        'postal_code': postal_code
                    }

                    # Update farmer data
                    result = update_farmer_data(contact_update)
                    if result:
                        st.success("✅ Contact information saved successfully!")
                        st.rerun()  # Refresh to show updated data
                    else:
                        st.error("❌ Failed to save contact information. Please try again.")

                except Exception as e:
                    st.error(f"❌ Error saving contact information: {str(e)}")
            else:
                st.error("❌ Email address is required")
