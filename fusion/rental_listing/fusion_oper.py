from sqlmodel import Session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.home_doc.service import HomeDocService
from entities.home_doc.repository import HomeDocRepository
from entities.common.enums import HomeDocCategoriesEnum, HomeDocTypeEnum, ListingStatusEnum, ListingTypeEnum
from entities.home_doc.models import HomeDoc
from pipeline.operation import Operation
from db.session import engine
from datetime import datetime
from typing import Dict, Any, List

from entities.residence.dtos import ResidenceCreate, ResidenceUpdate, ListingHistoryCreate, ListingContactCreate, ListingContactUpdate


class FusionOper(Operation):
    def __init__(self):
        super().__init__()

    def run(self, input_data):
        residence_repo = ResidenceRepository.get_instance()
        residence_srv = ResidenceService.get_instance(residence_repo)
        home_doc_repo = HomeDocRepository.get_instance()
        home_doc_srv = HomeDocService.get_instance(home_doc_repo)

        with Session(engine) as session:
            try:
                # =============================================================================
                # EXAMPLE 1: CREATE - Creating a comprehensive residence with all relationships
                # =============================================================================
                print("=== CREATE RESIDENCE EXAMPLE ===")

                # Construct DTO instances for nested objects first
                listing_agent_create = ListingContactCreate(
                    name="Sarah Johnson",
                    phone="+1-305-555-0123",
                    email="sarah.johnson@luxuryrealty.com",
                    website="https://sarahjohnson.luxuryrealty.com"
                )

                listing_office_create = ListingContactCreate(
                    name="Luxury Realty Miami",
                    phone="+1-305-555-9999",
                    email="info@luxuryrealty.com",
                    website="https://luxuryrealty.com"
                )

                listing_history_entries_create = [
                    ListingHistoryCreate(
                        event="Listed",
                        price=2500000.0,
                        listing_type=ListingTypeEnum.standard, # Use enum member directly
                        listed_date=datetime(2024, 1, 15),
                        days_on_market=0
                    ),
                    ListingHistoryCreate(
                        event="Price Reduced",
                        price=2350000.0,
                        listing_type=ListingTypeEnum.standard, # Use enum member directly
                        listed_date=datetime(2024, 3, 1),
                        days_on_market=45
                    )
                ]

                # The 'ListingCreate' DTO usually encapsulates the price, bedrooms, bathrooms, status
                # If your DTO expects a separate ListingCreate object, construct it here.
                # Based on dtos.py, ResidenceCreate directly takes price, bedrooms, etc.
                # So we won't need a separate ListingCreate DTO for the main fields directly within ResidenceCreate

                create_data = ResidenceCreate(
                    # Basic HomeDoc fields
                    external_id="EXT-12345",
                    interior_entity_key="luxury-villa-miami-2024",
                    category=HomeDocCategoriesEnum.ONE_STORY_HOUSE,
                    type=HomeDocTypeEnum.PROPERTY,
                    description="Stunning luxury villa with ocean views in Miami Beach",
                    extra_data=[
                        {"key": "view_type", "value": "oceanfront"},
                        {"key": "parking_spaces", "value": "3"},
                        {"key": "pool", "value": "yes"},
                        {"key": "elevator", "value": "no"}
                    ],

                    # ResidenceSpecsAttributes fields
                    area=450.5,
                    sub_entities_quantity=8,  # rooms count
                    construction_year=2020,

                    # HomeDocDimensions fields
                    length=25,
                    width=18,

                    # Listing fields
                    price=2500000.0,
                    hoa_fee=850.0,
                    bedrooms=4.0,
                    bathrooms=3.5,
                    status=ListingStatusEnum.active, # Use enum member directly

                    # Listing Agent (passed as a DTO)
                    listing_agent=listing_agent_create,

                    # Listing Office (passed as a DTO)
                    listing_office=listing_office_create,

                    # Listing History (list of DTOs)
                    listing_history=listing_history_entries_create
                )
                
                print("Status value to insert:", create_data.status) # Access as attribute
                print("Status value type:", type(create_data.status))
                print("Status enum value:", ListingStatusEnum.active.value)
                print("Status enum value:", ListingStatusEnum.active)
                print("Status enum value:", ListingStatusEnum)

                # Pass the DTO instance directly
                created_residence = residence_srv.create(create_data, session)
                print(f"Created residence ID: {created_residence.id}")
                print(f"Created residence key: {created_residence.interior_entity_key}")
                print(f"Created residence area: {created_residence.area} sqm")
                print(f"Created residence price: ${created_residence.listing.price:,.2f}")
                print(f"Agent: {created_residence.listing_agent.name}")
                
                # =============================================================================
                # EXAMPLE 2: GET BY ID - Retrieving a specific residence with all data
                # (No change needed here as it retrieves DTO from service)
                # =============================================================================
                print("\n=== GET BY ID EXAMPLE ===")
                
                retrieved_residence = residence_srv.get_by_id(created_residence.id, session)
                if retrieved_residence:
                    print(f"Retrieved residence: {retrieved_residence.interior_entity_key}")
                    print(f"Description: {retrieved_residence.description}")
                    print(f"Construction Year: {retrieved_residence.construction_year}")
                    print(f"Dimensions: {retrieved_residence.length}x{retrieved_residence.width}m")
                    print(f"Listing Status: {retrieved_residence.listing.status}")
                    print(f"Agent Email: {retrieved_residence.listing_agent.email}")
                    print(f"History entries: {len(retrieved_residence.listing_history)}")
                else:
                    print("Residence not found")

                # =============================================================================
                # EXAMPLE 3: GET WITH FILTERS - Advanced querying with multiple filters
                # (No change needed here as it takes a dict for query_params)
                # =============================================================================
                print("\n=== GET WITH FILTERS EXAMPLES ===")
                
                # Example 3a: Price range filter
                price_filter_params = {
                    "price[$gte]": 1000000,
                    "price[$lte]": 3000000,
                    "status": "active",
                    "limit": 10,
                    "sort": "-price"
                }

                
                expensive_residences = residence_srv.get(session, price_filter_params)
                if expensive_residences:
                    print(f" Found {len(expensive_residences)} expensive active residences")
                    for residence in expensive_residences[:3]:  # Show first 3
                        print(f"   - {residence.interior_entity_key}: ${residence.listing.price:,.2f}")
                
                # Example 3b: Area and construction year filter
                modern_large_filter = {
                    "area[$gte]": 300,
                    "construction_year[$gte]": 2015,
                    "bedrooms[$gte]": 3,
                    "category": HomeDocCategoriesEnum.ONE_STORY_HOUSE.value, # Use .value for query params
                    "sort": "-construction_year"
                }
                
                modern_houses = residence_srv.get(session, modern_large_filter)
                if modern_houses:
                    print(f"Found {len(modern_houses)} modern large houses")
                    for house in modern_houses[:2]:
                        print(f"   - {house.interior_entity_key}: {house.area}sqm, built {house.construction_year}")
                
                # Example 3c: Text search with LIKE operator
                search_filter = {
                    "description[$ILIKE]": "villa",
                    "description[$wildcard]": "both",
                    "limit": 5
                }
                
                villa_residences = residence_srv.get(session, search_filter)
                if villa_residences:
                    print(f"Found {len(villa_residences)} villas")
                    for villa in villa_residences:
                        print(f"   - {villa.interior_entity_key}")

                # Example 3d: Date-based filtering
                recent_filter = {
                    "created_at[$gte]": "2024-01-01",
                    "created_at[$date]": "true",
                    "sort": "-created_at"
                }
                
                recent_residences = residence_srv.get(session, recent_filter)
                if recent_residences:
                    print(f"Found {len(recent_residences)} residences created since 2024")

                # =============================================================================
                # EXAMPLE 4: UPDATE - Comprehensive update with relationship modifications
                # =============================================================================
                print("\n=== UPDATE RESIDENCE EXAMPLE ===")
                
                # Construct DTO instances for nested objects for update
                # For existing nested objects, you need their IDs.
                listing_agent_update = ListingContactUpdate( # Or ListingContactUpdate if you have it for partial updates
                    id=retrieved_residence.listing_agent.id, # Pass the existing ID
                    phone="+1-305-555-0124",  # Updated phone
                    website="https://sarahjohnson-updated.luxuryrealty.com"
                    # name and email are optional if not changing, but if DTO has them as required, include them
                )
                
                # The 'history' list needs to contain existing entries with their IDs,
                # and new entries without IDs.
                history_updates = []
                for entry in retrieved_residence.listing_history:
                    history_updates.append(
                        ListingHistoryCreate( # Use create DTO for both new and existing, passing ID for existing
                            id=entry.id,
                            event=entry.event,
                            price=entry.price,
                            listing_type=entry.listing_type,
                            listed_date=entry.listed_date,
                            days_on_market=entry.days_on_market
                        )
                    )
                # Add new entry
                history_updates.append(
                    ListingHistoryCreate(
                        event="Renovated & Re-listed",
                        price=2750000.0,
                        listing_type=ListingTypeEnum.standard, # Use enum member directly
                        listed_date=datetime(2024, 6, 1),
                        days_on_market=90
                    )
                )

                update_data = ResidenceUpdate(
                    # Update basic fields
                    description="UPDATED: Luxury villa with renovated kitchen and new pool",
                    extra_data=[
                        {"key": "view_type", "value": "oceanfront"},
                        {"key": "parking_spaces", "value": "4"},  # Updated
                        {"key": "pool", "value": "yes"},
                        {"key": "elevator", "value": "yes"},       # New feature
                        {"key": "renovated", "value": "2024"}      # New
                    ],
                    
                    # Update specs
                    area=475.0,  # Increased area after renovation
                    sub_entities_quantity=9,  # Added one more room
                    
                    # Update dimensions
                    length=27,  # Extended
                    width=18,
                    
                    # Update listing (if ListingUpdate DTO exists and expects these fields)
                    # Based on dtos.py, ResidenceUpdate takes a 'listing' object.
                    price=2750000.0,   # Price increase due to renovations
                    hoa_fee=950.0,     # HOA increase
                    bedrooms=5.0,      # Added bedroom
                    bathrooms=4.0,     # Added bathroom
                    status=ListingStatusEnum.active, # Use enum member directly
                    
                    # Update agent info (pass DTO)
                    listing_agent=listing_agent_update,
                    
                    # Add new history entry (list of DTOs)
                    listing_history=history_updates
                )
                
                # Pass the DTO instance directly
                updated_residence = residence_srv.update(created_residence.id, update_data, session)
                print(f"Updated residence ID: {updated_residence.id}")
                print(f"New area: {updated_residence.area} sqm")
                print(f"New price: ${updated_residence.listing.price:,.2f}")
                print(f"New bedrooms: {updated_residence.listing.bedrooms}")
                print(f"History entries after update: {len(updated_residence.listing_history)}")
                print(f"Agent updated website: {updated_residence.listing_agent.website}")

                # =============================================================================
                # EXAMPLE 5: BULK OPERATIONS - Multiple residences management
                # =============================================================================
                print("\n=== BULK OPERATIONS EXAMPLE ===")
                
                # Create multiple residences
                bulk_residences = []
                residence_templates = [
                    ResidenceCreate( # Use ResidenceCreate DTO
                        interior_entity_key="condo-downtown-01",
                        category=HomeDocCategoriesEnum.RESIDENTIAL_BUILDING,
                        type=HomeDocTypeEnum.PROPERTY,
                        description="Modern downtown condo with city views",
                        area=120.0,
                        construction_year=2018,
                        price=450000.0,
                        bedrooms=2.0,
                        bathrooms=2.0,
                        status=ListingStatusEnum.active
                    ),
                    ResidenceCreate( # Use ResidenceCreate DTO
                        interior_entity_key="townhouse-suburbs-02",
                        category=HomeDocCategoriesEnum.MULTI_STORY_HOUSE,
                        type=HomeDocTypeEnum.PROPERTY,
                        description="Family-friendly townhouse in quiet neighborhood",
                        area=180.0,
                        construction_year=2019,
                        price=650000.0,
                        bedrooms=3.0,
                        bathrooms=2.5,
                        status=ListingStatusEnum.active
                    )
                ]
                
                for template in residence_templates:
                    try:
                        # Pass the DTO instance directly
                        residence = residence_srv.create(template, session)
                        bulk_residences.append(residence)
                        print(f"Created: {residence.interior_entity_key} - ${residence.listing.price:,.2f}")
                    except Exception as e:
                        print(f"Failed to create {template.interior_entity_key}: {e}") # Access as attribute

                # =============================================================================
                # EXAMPLE 6: ADVANCED FILTERING AND ANALYTICS
                # (No change needed here as it takes a dict for query_params)
                # =============================================================================
                print("\n=== ADVANCED ANALYTICS EXAMPLE ===")
                
                # Get all active listings for market analysis
                market_analysis_filter = {
                    "status": ListingStatusEnum.active.value, # Use .value for query params
                    "price[$gte]": 100000,  # Minimum reasonable price
                    "area[$gte]": 50,       # Minimum reasonable area
                    "limit": 100,
                    "sort": "price"
                }
                
                market_residences = residence_srv.get(session, market_analysis_filter)
                if market_residences:
                    print(f"Market Analysis - {len(market_residences)} active listings:")
                    
                    # Calculate average price per sqm
                    total_price = sum(r.listing.price for r in market_residences if r.listing.price)
                    total_area = sum(r.area for r in market_residences if r.area)
                    avg_price_per_sqm = total_price / total_area if total_area > 0 else 0
                    
                    print(f"   Average price per sqm: ${avg_price_per_sqm:,.2f}")
                    
                    # Price ranges
                    prices = [r.listing.price for r in market_residences if r.listing.price]
                    if prices:
                        print(f"   Price range: ${min(prices):,.2f} - ${max(prices):,.2f}")
                        print(f"   Average price: ${sum(prices)/len(prices):,.2f}")

                # =============================================================================
                # EXAMPLE 7: ERROR HANDLING AND VALIDATION
                # =============================================================================
                print("\n=== ERROR HANDLING EXAMPLES ===")
                
                # Try to create invalid residence (should fail validation)
                try:
                    invalid_data = ResidenceCreate( # Use ResidenceCreate DTO
                        interior_entity_key="invalid-residence",
                        category=HomeDocCategoriesEnum.ROOM_KITCHEN,   # Invalid for residence
                        type=HomeDocTypeEnum.PROPERTY,
                        description="This should fail",
                        # Provide dummy required fields, or the DTO validation will fail first
                        price=1.0, bedrooms=1.0, bathrooms=1.0, status=ListingStatusEnum.active
                    )
                    residence_srv.create(invalid_data, session)
                except Exception as e:
                    print(f"Validation error caught: {e}")
                
                # Try to get non-existent residence
                non_existent = residence_srv.get_by_id(99999, session)
                print(f"Non-existent residence result: {non_existent}")
                
                # Try to update non-existent residence
                try:
                    # Need to provide a valid ResidenceUpdate DTO even for a non-existent ID
                    # The service will likely raise an error when the ID is not found.
                    residence_srv.update(99999, ResidenceUpdate(description="test"), session)
                except Exception as e:
                    print(f"Update error caught: {e}")

                # =============================================================================
                # EXAMPLE 8: DELETE OPERATION
                # =============================================================================
                print("\n=== DELETE OPERATION EXAMPLE ===")
                
                # Delete one of the bulk created residences
                if bulk_residences:
                    residence_to_delete = bulk_residences[0]
                    print(f"Deleting residence: {residence_to_delete.interior_entity_key}")
                    
                    # Verify it exists before deletion
                    before_delete = residence_srv.get_by_id(residence_to_delete.id, session)
                    print(f"Before delete - exists: {before_delete is not None}")
                    
                    # Delete
                    residence_srv.delete(residence_to_delete.id, session)
                    
                    # Verify deletion
                    after_delete = residence_srv.get_by_id(residence_to_delete.id, session)
                    print(f"After delete - exists: {after_delete is not None}")

                print("\n=== ALL EXAMPLES COMPLETED SUCCESSFULLY ===")

            except Exception as e:
                print(f"Error in FusionOper: {str(e)}")
                raise