# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.10.5] - 2022-06-03
- Added feature to allow users to compete in competitions

## [2.10.4] - 2022-04-27
- Project tiles stay visible even when video is uploaded
- Allow projects to be hidden under charities but stay visible if promoted

## [2.10.3] - 2022-04-12

### Changed

- Users profile page displays amounts donated per project

## [2.10.2] - 2022-02-14

### Fixed

- Fixed missing CSRF token on second donation without a page refresh
- Fixed visibility of receipt icon on suppliers
- Fixed order of promoted projects

## [2.10.1] - 2022-02-14

### Fixed

- Bug in `ReceiptingReport`

## [2.10.0] - 2022-01-17

### Changed

- Charities "promote" their own projects by adding the relevant information to query strings

## [2.9.5] - 2022-01-14

## [2.9.4] - 2022-01-11

### Fixed

- Projects do not use catalog prices at all, so do not filter on catalog prices

### Customer changes

- Promoted projects that disappeared from the brand pages are back.

## [2.9.3] - 2022-01-07

### Changed

- Include charities in the batch branded vendor restriction options.

## [2.9.2] - 2022-01-04

### Added

- After donation redirect url to product extra.

### Changed

- Forms, templates, macros to handle the after donation redirect url.

### Customer changes

- Projects can specify a url to redirect a donor to after a successful donation.

### Fixed

- Bug in GivesomeBaseBrandView.

### Customer changes

- Organizations can optionally specify a URL to redirect donors to after a donation is made.

## [2.9.1] - 2022-01-03

### Added

- Implemented continued givers aggregate in Campaign Reports

## [2.9.0] - 2021-12-23

### Updated

- Update to shuup 3


### Fixed

- Fix contact messages form

## [2.8.9] - 2021-12-09

### Fixed

- Translation formats
- Missed translation calls

## [2.8.8] - 2021-12-09

### Added

- More translations

### Fixed

- Extra "$" in "Thank you for your donation" modal
- Made more strings translatable

## [2.8.7] - 2021-12-08

### Updated

- Add more translations

## [2.8.6] - 2021-12-08

### Fixed

- Bug in admin that prevented child offices from saving.

## [2.8.5] - 2021-12-07

### Fixed

- Projects (Products) should default to Not Shipped
- Givecard receipt label translates correctly
- Update label to be translatable

## [2.8.4] - 2021-12-06

### Fixed

- Cached projects are aware of current active language

## [2.8.3] - 2021-12-03

### Changed

- Bump shuup-stripe-multivendor (for translations)

## [2.8.2] - 2021-12-03

### Added

- French translations

### Fixed

- Receipting message language cache awareness
- Made some strings translatable

## [2.8.1] - 2021-12-02

### Updated

- Added some French translations

### Fixed

- Made some strings translatable

## [2.8.0] - 2021-12-02

### Added

- New receipting messages
- Additional styling to login page during receipting process

### Changed

- Anonymous and freshly-registered users get 4 minutes of receipting "memory"

## [2.7.21] - 2021-11-18

### Changed

- Cast receipting report amounts to floats from Decimals

## [2.7.20] - 2021-11-17

### Fixed

- Shipping address fields are not required
- Billing postal code is required

## [2.7.19] - 2021-11-16

### Fixed

- CRONJOBS is an empty list for now
- Don't attempt a currency conversion (and then break) if the user has no preference

### Changed

- Customer information buttons rearranged
- Firebase login wording adjusted for receipting process
- Address form labels, required fields adjustments
- Made certain error messages more user-friendly

## [2.7.18] - 2021-11-12

### Fixed

- Anonymous receipting session data is "recalled" after registering a new user

### Changed

- Ready to go: users may choose a preferred currency and see/donate in that currency

## [2.7.17] - 2021-11-02

### Changed

- Receipting tooltip in product card shows on first tap

## [2.7.16] - 2021-10-19

### Fixed

- Staff users no longer fail project ordering validation

## [2.7.15] - 2021-10-13

### Changed

- Removed 15-project slice of projects on profile page

## [2.7.14] - 2021-10-08

### Changed

- Updated receipting image file

### Fixed

- Receipting modal doesn't completely overwhelm mobile screens
- Receipting modal is closeable on mobile screens
- GivesomeVendorForm is no longer re-overridden by VendorForm

## [2.7.13] - 2021-10-05

### Changed

- Receipting icons on projects pages, cards render based on receipting settings

## [2.7.12] - 2021-10-04

### Fixed

- Brands don't have registration numbers

## [2.7.11] - 2021-10-04

### Changed

- Previously receipting-enabled projects appear disabled if its charity is disabled

### Fixed

- Fix 500 error when trying to render a receipting variable for a misconfigured charity

## [2.7.10] - 2021-10-01

### Fixed

- Charity registration number no longer required on form, skip validation if missing
- Check charity and project receipting setting when rendering donation form

### Changed

- ReceiptingMessages CharFields changed to TextFields

## [2.7.9] - 2021-09-27

### Added

- Static off-platform totals
- Introductory modal explaining receipting to end users

### Changed

- Charity registration number not required

## [2.7.8] - 2021-09-24

## [2.7.7] - 2021-09-23

### Fixed

- Brand name key in report schema
- Charity projects display on charity detail page.

### Added

- Staff users can enable/disable receipting for charities
- Enabled charities can enable/disable receipting for projects
- Hide receipting option from donors if disabled
- Fields/AJAX/view for brands and offices to order their promoted products
- Brand and office pages render project cards in their assigned order
- Offices filtering in Givecard reports

## [2.7.6] - 2021-09-21

### Fixed

- Fix checkout gif background-image url

## [2.7.5] - 2021-09-17

### Fixed

- Re-open donation modal if users decides against completing profile information

## [2.7.4] - 2021-09-17

### Fixed

- 'Undefined' donation amount
- Auto-check custom donation radio choice on KeyUp event
- Remove all receipting info from the session upon realizing that time is up
- Handle receipting wishes (True, False, None) correctly

### Customer Changes

- The "Thank you for your $n contribution" modal shows the correct amount.
- Custom donation amount choice is checkable again
- Receipting fixes

## [2.7.3] - 2021-09-17

### Changed

- Ignore receipting process in session after 2 minutes

### Fixed

- init_project bug
- New off-platform donations now appear at the top.
- Off-platform doantions are sorted in reverse chronological order.
- Vendors are set up with Simple Supplier again
- Logged in users who want a receipt and have incomplete profiles correctly go to profile completion
- Receipting timestamp check
- Don't crash if abandoning receipting process altogether under some conditions

### Added

- Charity filter on Receipting Report

### Customer changes

- New off-platform donations now appear at the top.
- Off-platform doantions are sorted in reverse chronological order.
- Staff users can filter Receipting Reports by charity
- Receipting process remembers where the user should go next for 2 minutes instead of 3

## [1.7.2] - 2021-09-08

### Fixed

- Fixed receipting message caching

## [1.7.1] - 2021-09-08

### Fixed

- Fixed wheel

## [1.7.0] - 2021-09-08

### Added

- Stripe Donation report (for receipting)
- Registration ID field for charities
- Receipt message management in admin
- Receipt icon/messages render on pages
- Receipting eligibility checks to login
- Receipting eligibility checks to profile edit
- Receipt request to donation form

### Customer changes

- Receipting info
- Can request a receipt when donating

## [1.6.7] - 2021-09-01

### Added

- Add so admin can change the checkout gif from admin panel

## [1.6.6] - 2021-09-01

### Fixed

- Fix large donations

## [1.6.5] - 2021-09-01

### Fixed

- Fix so when exiting donate modal it will clear the values

## [1.6.4] - 2021-08-19

### Fixed

- Charity Weblink button to scale to text size

## [1.6.3] - 2021-08-04

### Removed

- Don't sync permissions when deploying

### Added

- Redirect to specified office after redemption (if applicable)

## [1.6.2] - 2021-07-30

### Changed

- Bump Shuup to 2.13.0

### Fixed

- Fix `init_project` management commend for Brand Purse feature

Enter here all the changes made to the development version

## [2.6.1] - 2021-07-22

### Fixed

- Correctly transfer funds from AUTOMATIC expiry batches to purses

## [2.6.0] - 2021-07-21

### Added

- Allow Vendors to have a Brand-purse
- Brand-purse can be enabled or disabled
- Project image to Purse manual donation page
- Improved validation when creating manual donations
- Support to handle expired Givecard batches for layers of offices
- Support for Brand-Purses when handling expired Givecard batches
- Support filtering by Purse in Purse-related reports
- Total row to Purse-related reports
- Allow customers to enter a Mailing Address

### Changed

- Modify Purse-module to allow selecting Givesome or Brand purses
- Tune Admin and Vendor admin menus to be more intuitive
- On Office page in office dropdown menu indent offices based on level

### Fixed

- Fixed user being redirected to nonexistent page after creating a manual purse donation
- OfficeListView show correct columns
- Off-platform hours and donations columns being swapped on Vendor Dashboard
- Givecard Donation Report individual Givecard donation amounts

### Removed

- Irrelevant reports

## [2.5.2] - 2021-07-20

### Added

- Filter available parent offices dynamically after selecting a supplier

## [2.5.1] - 2021-07-19

### Added

- Givecards restricted to an office include office's descendants as valid
- Use Office level to determine consumed cards in checkout
- Redirect Office -field to Givecard Batches

### Changed

- Display all ancestors for an office instead of just the supplier
- Improve Givecard Batch list column values

### Fixed

- Trying to donate with a Givecard with an office restriction and no office set failing
- Project `sponsored_by` initial value not being filled
- Project stock adjustment
- Breadcrumbs on project pages

## [2.5.0] - 2021-07-15

### Added

- Admin: Allow setting office a parent office
- Admin: Allow setting different `Office Terms` for each level of offices
- Admin: Allow disabling an office, which disables all of its children
- Front: Use levels of offices to display offices hierarchically
- Front: Hide disabled offices

## [2.4.1] - 2021-07-14

### Changed

- Allow Givecard Batch value to be modified even if Batch has redeemed Givecards
- Restyle vendor dashboard

## [2.4.0] - 2021-07-12

### Added

- Add Available From field to projects

### Changed

- Vendor Dashboard small changes based on feedback

## [2.3.0] - 2021-07-05

### Added

- Allow altering Givecard Batch quantity and value
- Allow charities to promote other charities projects
- Xtheme plugin to allow selecting featured projects videos and their order

## [2.2.1] - 2021-07-01

### Added

- Display Campaign "Continued Giving" data in Vendor Dashboard

### Changed

- Display Vendor Dashboard aggregate blocks only if group has over 1 campaign
- Made weblink button wrap on mobile reduce font size
- Make project card logos larger on homepage

## [2.2.0] - 2021-06-23

### Added

- Group-field to Givecard Campaigns
- Group Campaigns in vendor dashboard by their Group-field

### Fixed

- Issues with Project selection plugins before config was saved

## [2.1.2] - 2021-06-22

### Fixed

- Improve performance in Vendor Dashboard by a ton
- Fix Campaigns being hidden that had a single archived batch
- Sponsored By not being visible on vendor pages
- Removed unnecessary commas from vendor addresses

## [2.1.1] - 2021-06-22

### Fixed

- Management command to migrate orders from "projects table" for a few edge case projects

## [2.1.0] - 2021-06-21

### Added

- Add new plugin so product selection plugin can be ordered
- Campaign filter to Campaign Summary report
- `Archived`-field to Campaign and Batch
- Only display non-`Archived` Campaigns and Batches in Vendor Dashboard

### Changed

- Change so "sponsor by" is visible on both VendorExtraType vendors

### Fixed

- Not being able to save a Batch without setting a Campaign
- Getting Campaign total donated amounts

## [2.0.17] - 2021-06-17

### Added

- Management command to migrate more donations from old platform database dump

## [2.0.16] - 2021-06-15

### Fixed

- Fix Givecard redemption date filter

## [2.0.15] - 2021-06-15

### Added

- Allow adding a description to Project Completion Videos

### Fixed

- Fix Givecard redemption date filter

### Changed

- Hide Campaigns with no donations in Campaigns report
- Move GivesomePurse balance from a field to a method

## [2.0.14] - 2021-06-10

### Fixed

- Bump xtheme plugin cache on successful donation
- Report filters not being shown or used

## [2.0.13] - 2021-06-02

### Fixed

- Fix donate button not getting enabled on mobile
- Fix user being redirected twice to next_url
- Fix error message when anonymous users' givecards were stolen

### Changed

- Change donation `Not enough Givecard funds` message

## [2.0.12] - 2021-06-02

### Added

- Donation value of submission button to display on input change
- Management command to migrate missing orders

### Fixed

- Assign migrated givecards to a user
- Update migrated givecard balance to match spent funds

### Changed

- Display all projects donated to, even unapproved, on user profile page
- Modify some migrated givecard expiry dates

## [2.0.11] - 2021-05-27

### Fixed

- Fix annotating redeemed givecard percentage being broken in some cases

## [2.0.10] - 2021-05-26

### Fixed

- Improve vendor dashboard performance a lot

## [2.0.9] - 2021-05-26

### Fixed

- Improve vendor dashboard performance a little

## [2.0.8] - 2021-05-25

### Fixed

- Fix getting promoter ID from query parameters

## [2.0.7] - 2021-05-24

### Added 

- Add command to migrate missed Givecards from firebase export file
- Vendor Type column to VendorListView

### Fixed

- Fix breaking when getting promoter ID if user modified the URL

## [2.0.6] - 2021-05-20

### Added 

- Commit npm-shrinkwrap
- Commit images

### Fixed

- Fix enabling donate button

## [2.0.5] - 2021-05-20

### Added 

- Styles to vendor website link button
- More warning messages related to Givecards when donating to Projects

### Changed

- Always show full vendor description, remove `Show more` button
- Use prettier website link on vendor pages
- Consider `Listed` and `Searchable` Projects as Completed in Customer Dashboard
- Disable donations for `Listed` and `Searchable` Projects
- Do not automatically create vendors when running `init_project`

### Fixed

- Project card 2 line text
- Increase vendor logo size on project card
- Hide Fully Funded projects from `Other Projects Promoted by ...`
- Force Firebase login hidden if user is logged in
- Vendor dashboard blocks trying to display `None` values
- Fix `website url` being mandatory, when it shouldn't be

## [2.0.4] - 2021-05-17

### Added

- Display Vendor URL on vendor page

### Changed

- Modify campaign * text verbiage
- Modify "Sign in" verbiage
- Order projects by most recent donation first on Customer Dashboard

### Fixed

- Small rounding error on Givecard Batch Used Percentage

### Removed

- 'Last donation'-text on project cards and page

## [2.0.3] - 2021-05-11

### Fixed

- Vendor dashboard total donated

## [2.0.2] - 2021-05-10

### Changed

- Simplify customer dashboard
- Givecard file structure refactoring

### Fixed 

- Fix `givesome-app` and `givesome-admin` references to `givesome-marketplace`
- Vendor Dashboard values
- Givecard Campaign and Batch summary values

### Removed

- Facebook login button

## [2.0.1] - 2021-05-05

### Fixed

- Poetry related stuff

## [2.0.0] - 2021-05-05

### Changed

- Merge `givesome-app` and `givesome-admin` into a single `givesome-marketplace` wheel.

---

## [1.3.72] - 2021-05-04

### Added

- Redirect user to brand page if they weren't redirected earlier after givecard redemption

### Fixed

- Saving products due to supplier validation error

## [1.3.71] - 2021-04-22

### Fixed

- Vendor campaign dashboard redeemed percentage

## [1.3.70] - 2021-04-22

### Fixed

- Incorrect values in vendor campaign dashboard

## [1.3.69] - 2021-04-19

### Changed

- Always display $ as donated currency in checkout

## [1.3.68] - 2021-04-15

### Fixed

- Fix getting new product suppliers causing an error

## [1.3.67] - 2021-04-15

### Fixed

- Error caused by missing campaign in an already redeemed Givecard 

### Changed

- Project Cards logo size increased

## [1.3.66] - 2021-04-14

### Fixed

- Incorrectly display Givecard checkout as usable in some cases

## [1.3.65] - 2021-04-14

### Added

- More error messages when user fails to redeem a Givecard
- Display more of Charity's projects on project page

### Changed

- Don't redirect user to the same page they are on when redeeming a Givecard

### Fixed

- Add extra validation on checkout donation amounts
- Hide unapproved projects in customer portfolio
- Verify order product is added to basket before creating an order
- Project promoter being improperly selected sometimes
- Charities with Branded Pages not having their brand visible on product page
- Correctly disable vendor type field in admin
- Initial selected charity on vendors

## [1.3.64] - 2021-04-09

### Added

- Add Brand Vendor dashboard for Givecard Campaigns

### Fixed

- Use shop currency in stripe checkout

### Changed

- Admin module where staff can choose and order Featured Projects

## [1.3.63] - 2021-04-09

### Fixed

- Removed unwanted cropping of campaign images
- Selection of radio btn containers in Givecard donation modal not working for PIN type donation
- Saving a project does not delete the completion video(s)
- Use shop currency whenever possible instead of settings currency
- Fix office breadcrumbs vendor link

### Changed

- Staff users can set project to be featured

## [1.3.62] - 2021-04-07

## Fixed

- Use app version for static files

## [1.3.61] - 2021-04-07

## Fixed

- Fix redeeming Givecard when shown expiring codes is null 

## [1.3.60] - 2021-04-07

### Fixed

- Error caused by office term in Office Page
- Force currency to CAD
- CMS URL links in front

## [1.3.59] - 2021-04-07

### Added

- French translations

### Fixed

- Do not display expiry modal for same-session redeemed givecards

## [1.3.58] - 2021-04-06

### Added

- Sponsored by fields to suppliers and projects

### Changed

- Use `batch_size` and `bulk_update` with `batch_size` when migrating data.
- On paying for donations radio button is selected via it's container and not the label
- My Account to My Profile in nav dropdown
- Allow changing vendor type in more cases

### Fixed

- Use default term "Project" in case of no project term set
- Clicking user link goes to profile and if on profile page already displays a dropdown to let user logout
- Redeeming Givecards with supplier restriction who has disabled brand page

## [1.3.57] - 2021-04-02

### Fixed

- Reduce data migration memory footprint

## [1.3.56] - 2021-04-02

### Changed

- Remove product breadcrumbs that led to category page
- Clear Modal warnings on modal close
- Disable arrows on number input fields
- Always show "Redeem new pin" button

### Fixed

- Display of projects on office page
- Carousel overflow and not scaling to mobile

## [1.3.55] - 2021-04-01

### Fixed

- Order integer skus as integers in givesome data migrator

## [1.3.54] - 2021-04-01

### Added

- Vendor ordering

### Fixed

- Guarantee a unique product sku during project migration
- Admin product edit form by blacklisting original form
- Sponsored By wording
- Issues with Givecards saving incorrectly to session wallet
- Incorrectly clearing authenticated user session wallet

### Changed

- Show one checkout method Givecard/Stripe based on user Givecards
- Disable Media Browser on New Product creation

## [1.3.53] - 2021-03-30

### Added

- Display more offices under office pages
- New warning on failed givecard checkout if actual balance is less than expected balance

### Changed

- Hide Givecard Batch Delete button if Givecards in batch have been used

### Fixed

- Fix projects goal progress to always round down
- Update wallet properly after checkout
- Authenticated user givecard wallet caching issues

## [1.3.52] - 2021-03-26

### Changed

- Nav only shows user dropdown if on dashboard view
- User nav Link routes to profile onclick
- language and verbage per request

### Fixed

- image stretching on logos
- footer logo styling

## [1.3.51] - 2021-03-25

### Added

- Random partner company logo at the bottom of some pages
- Automated migration of existing client data

### Changed

- Added links to banner logos
- Simplified vendor URLs

### Fixed

- Font sizes / styling coherency
- Logo display in browse sections
- variation image alignment
- User name's displaying incorrectly in nav and profile
- Anynomous users sometimes having givecards in wallet they didn't redeem
- Bump product qs cache when promoting projects
- Office filter for suppliers in Batch Edit View

### Removed

- hid filter displays

## [1.3.50] - 2021-03-22

### Added

- Random partner company logo at the bottom of some pages
- Automated migration of existing client data

### Changed

- increased logo size on homepage plugins
- footer alignment and spacing
- charity page banner and sponsered by spacing
- VolunteerHours and OffPlatformDonation form labels updated
- Removed grayscale filter from homepage logos

### Fixed

- vendor_type field in Vendor Edit Page
- Don't migrate users who already exist

## [1.3.49] - 2021-03-09

### Added

- More filters to Givecard batches and Campaigns
- `created_on` field to Givecard Campaign
- Vendor Project Promote Module

### Fixed

- Givecard Batch filters
- `Product added to cart` text on most pages
- Error caused by missing translations when deleting objects
- Added MySQL support for CompletionVideos qs
- VolunteerHours and OffPlatformDonations are filtered by PersonContact
- VolunteerHours and OffPlatformDonation forms correctly show errors for missing required fields
- "Edit Profile" link goes to dashboard

### Changed

- Specific words requested by customer
- Remove digits from generated Givecard codes
- Redirect user to root instead of profile on login

## [1.3.48] - 2021-03-04

### Fixed

- Unique Givecard Batch Edit Page having code field

## [1.3.47] - 2021-03-04

### Fixed

- Errors caused by missing stock amounts on older projects
- Better error handling for Givecard Campaign identifiers

## [1.3.46] - 2021-03-03

### Changed

- Various wording updates per client specs
- Hide Street and Post code in vendor registration

### Fixed

- `favorites_only` UndefinedError
- Description field text editors in admin
- Footer vendor registration links
- Add website_url to vendor edit page

## [1.3.45] - 2021-03-02

### Added

- Capability to "nullify" expired, Manual type batches
- Basic project info added to Givesome Purse Manual Donation page

### Fixed

- Office project promotion no longer broken
- Custom report filters not causing an error
- Create project_extra if missing in product edit view
- Code missing from Multicard Batch edit

## [1.3.44] - 2021-02-25

### Added

- Vendor Primary Project admin module
- Filters for Givecard Campaign Summary Report
- Many custom reports
- More tracking data for automatic and manual admin/vendor donations

### Fixed

- Donation quantities on Thank You modal are correct
- "Donate" btn re-shown after Stripe donation
- Stripe form shown without refreshing after all givecards have been donated
- Givecards not updated in wallet after checkout
- Use timezones wherever dates are used
- Batch Edit page javascript

## [1.3.43] - 2021-02-24

### Added

- Givesome Purse Module
- Givesome Purse manual donation to projects
- Allocate funds from expired Givecard Batches to Givesome Purse
- Off platform giving on user profile
- Link to charity registration
- Spinner to Givecard redemption modal
- Givecard Campaign Summary Report

### Fixed

- Hide Stripe checkout form if givecard donation is possible
- Fix server error when donating to funded projects from stale pages
- Incorrectly sized project cards on project detail page
- Project breadcrumbs trace back to brand
- Redirect admin and staff to correct admin dashboard
- Make sure orders are set complete when creating automatic orders from expired Givecards
- Remove project promotions from hidden and unapproved projects
- Show "Donate" btn after a Stripe donation without refreshing the page
- Stripe donation thank you reports correct amount when Givecard amount is also selected

### Changed

- Givecard batches download in xlsx format
- Create separate PurchaseReportData for each Givecard Payment when multiple is used

## [1.3.42] - 2021-02-10

### Added

- Show a warning when Givecards expire in wallet
- Summary pages to Givecard Campaign and Batch
- Filtering vendors by favorites
- Allow Enter as a valid redemption submit event
- Go to donation page on redemption success modal hidden event

### Changed

- Project page displays more projects instead of Charity information

### Fixed

- GIVESOME-QA-X: KeyError when a redeemed givecard has no expiration date
- Show expiring Givecards warning if any new Givecards are expiring
- Hide expired Givecards in wallet
- Incorrect initial button text when selecting office Primary Project

## [1.3.41] - 2021-02-09

### Added

- Staff can download Givecard data by the batch
- Allow offices to select a primary project in project promotion view
- Coffee icons to checkout
- Management command to reallocate expired Givecard balances

### Fixed

- Completion video links delete correctly in admin
- Display latest video on profile, not first video

## [1.3.40] - 2021-02-02

### Added

- Users are invited to subscribe to the charity after donation
- Charity subscription pages/cards
- On Givecard Redeemed warn if Givecard is expiring soon
- Completion videos on donor profile, homepage carousel

### Changed

- Charity registration sets up a product (et al) for use later
- JS checkout code refactored
- Data for purchase reports is now stored in the db
- Always display Givecard expiry date

### Fixed

- GIVESOME-QA-T issue: TypeError on checkout form load

## [1.3.39] - 2021-01-29

### Changed

- Group Givecards in wallet by Campaign first
- Use Givecard Campaign name when naming Givecards in wallet
- Modify Givecard Redeemed modal style
- Display Campaign Supplier instead of Batch Supplier when givecard is redeemed
- Use Givecard Batch restriction type when grouping Givecards
- Universal Givecards link to `/` instead of `supplier_list`

## [1.3.38] - 2021-01-28

### Added

- Completion Videos section in product edit page.
- Staff and Charities can add multiple YouTube links to projects
- The most recent link is embedded in the product edit page for user to preview
- Hide stripe checkout if the user can donate via givecard
- Givecard Wallet async support
- Restriction and Expiry fields to Givecard Batch

### Fixed

- Stripe checkout ui toggles custom inputs correctly
- Put all stripe checkout ui logic into one place
- Create givesome_extra when creating a vendor through admin backend
- Wallet cache showing old wallet data in some cases

### Changed

- Enable using numbers in Givecard and Batch Codes
- Allow numbers in Givecard codes

## [1.3.36] - 2021-01-21

### Added

- List of profane words for Givecard code profanity filter
- Initial Givecard checkout

### Changed

- Notify if Givecard is expiring in a week

## [1.3.35] - 2021-01-18

### Changed

- Move offices under projects list

## [1.3.34] - 2021-01-15

### Fixed

- Radio inputs don't disappear after donating
- 'Pay with' button reflects user input more accurately

## [1.3.33] - 2021-01-15

### Added

- Profanity filter to generated givecards
- Show Expiring Givecards modal when user logs in, and they have expiring Givecards in their wallet

### Fixed

- Show supplier and office restrictions in Givecard wallet for authenticated users

## [1.3.32] - 2021-01-14

### Added

- Add branding to project page iff user arrived from a promoting brand/office page
- Add reporting data to `order.extra_data`.
- Add social media sharing after donating


## [1.3.31] - 2021-01-14

Beautify checkout process

- Update styles on checkout amount selection
- Add confetti animation
- Update styles on the checkout success modal
- Add meta og:image for a project

## [1.3.30] - 2021-01-14

### Added

- Display a warning in wallet for expiring funds
- Update wallet button when first Givecard is redeemed
- Caching for Givecard wallet
- Setting for Multicard grace period length
- Disabled Multicard re-redemptions
- Offer account creation to anonymous donors to see their impact

### Fixed

- Unique Givecards using Multicard grace period when they shouldn't

### Changed

- Givecard Batch redeemable and expiry fields use date instead of datetime
- Generate Givecards when GivecardBatch is saved

## [1.3.29] - 2021-01-13

### Added

- Custom UI for Givesome progress adjustments

## [1.3.28] - 2021-01-12

### Fixed

- New projects require a supplier

### Added

- Filter Office options based on selected Supplier in Givecard Batch Edit
- Display modal with campaign message when givecard is successfully redeemed
- Improvements Givecard and GivecardBatch lists
- Link user to restricted office page on Givecard Redemption

## [1.3.27] - 2021-01-08

### Fixed

- `lives_impacted` accessible to both staff and charities

## [1.3.26] - 2021-01-08

### Added

- Add support for saved cards

### Fixed

- Projects no longer apply donation to goal on some stripe errors.

### Added

- Add redeemed Givecards to session storage
- Render redeemed Givecards in wallet
- Add redeemed Givecards to users wallet, update wallet total balance
- Show Givecard redeeming success modal
- Givecard wallet is populated when user logs in
- Calculate total wallet balance
- Group Givecards in wallet by Supplier, Office, Balance

### Fixed

- Redeeming multiple unique code Givecards from the same batch when authenticated

## [1.3.25] - 2021-01-05

### Added

- Added a lot of error handling, and moved Givesome processing so that donations
aren't counted toward goals until after the AJAX conversation with Stripe.
- Funded and "Coming Soon!" projects can't receive donations.

## [1.3.24] - 2021-01-05

### Added

- Givecard Campaign Module
- Givecard Batch Module
- Givecard generation
- Givecard redemption logic
- Separate pages for creating Multicards and Unique Givecards
- 'Last Donation' calculations
- Custom donation logic'

### Changed

- Hide fully funded projects in office project promotion
- SKUs start from 1000
- Simplify admin backend

## [1.3.23] - 2021-01-04

- Display checkout form always in the modal window without
  a need to click a title to display it
- Add error message at checkout
- Show donate button again after failed form submit
- Change font on stripe card element

## [1.3.22] - 2020-12-31

### Fixed

- shuup-stripe-multivendor basket fix doesn't break checkout

## [1.3.21] - 2020-12-30

### Added

- SDG selection dropdown doesn't require typing 3 characters anymore
- Order Offices by ordering field
- Vendor Type selection to front page vendor plugin
- Link to Project Page in admin ProjectPromote
- Givecard generation, validation and tests
- Givecard Batch, date validation and tests
- Custom Stripe checkout process

### Changed

- Don't allow project supplier to be changed

### Fixed

- Don't link to charity vendor page when their page is not enabled

## [1.3.20] - 2020-12-04

### Added

- Allow branded vendors to create and manage offices
- Allow adding SDGs to offices
- Allow offices to promote projects
- Add staff support for offices and project promotion
- Add pages for offices in front
- List offices in branded vendor pages
- Add SDG filter to Supplier and Office pages

### Changed

- Vendor page displays all projects promoted by their offices

### Removed

- Disallow branded vendors to promote projects themselves

## [1.3.19] - 2020-12-09

### Added

- Charity brand pages display their associated SDGs.
- Took SDG info text from original Givesome site.
- Fixed case where cached value for Vendor Information pages is an empty queryset.

## [1.3.18] - 2020-12-08

### Added

- Make project progress functional through stocks
- Display project progress in front
- Display project progress in admin product list
- Notification Event for fully funded projects for charities
- Shop Setting for how many days to display a fully funded project in front
- Use Fully Funded Date to exclude projects in Vendor and Categories pages, Project Highlights carousel
- Custom admin module allows staff to create static content for vendors only
- Conditionally rendered links to vendors-only content in footer
- Projects can't be donated to if goal is reached

## [1.3.16] - 2020-12-03

### Added

- Vendors (and staff) can add a color choice to be applied to the vendor's brand page.

## [1.3.15] - 2020-11-25

### Added

- Staff users can grant/revoke Branded Page rights to vendors
  via Vendor Management

### Fixed

- Promote projects vendor filter
- Supplier view cache issues
- Bump supplier cache when project is promoted

## [1.3.13] - 2020-11-23

### Added

- Vendors, charities, projects can be associated with SDGs
- Charity sign-up creates a Plan for monthly donations

### Fixed

- Saving vendor and project without any SDGs set

## [1.3.12] - 2020-11-19

### Fixed

- Category filter on vendor page, when no categories exist

## [1.3.11] - 2020-11-19

### Added

- Rich text editor and HTML for product descriptions
- Product category filter to charity and brand vendor pages
- Separate registration pages for charity and brand vendors
- Assign correct permissions to vendors on registration

## [1.3.10] - 2020-11-17

### Added

- Partner and Charity vendor pages
- Display promoted projects in Partner pages
- Shop setting to allow promoting invisible projects

## [1.3.7] - 2020-11-13

### Added

- Charity registration (extended from existing vendor registration)
- Custom SustainabilityGoal model and admin functionality
- Allow branded vendors to select projects to be promoted

### Changed

- Initial project settings to not require shipping method
- Updated initial permissions
- Limit products to have one category

### Removed

- Unnecessary installed apps
- Unnecessary fields from products
- Shipping details in orders
- Other unnecessary features

## [1.3.4] - 2020-11-02

### Added

- Add Firebase authentication.
- Set product and shipping tax in
- Use different log in and sign up texts on /auth/ page.

### Changed

- Make CA and CAD be the default country and currency
- Update default permissions

## [1.3.2] - 2020-10-26

- Definite theme bump

## [1.3.1] - 2020-10-15

- Fix blacklisted items
- Update permissions to include orders for staff and vendors
- Allow unapproved vendors access to admin
- Update init project script

## [1.3.0] - 2020-10-02

### Added

- Add and configure shuup-sitemaps to the project

## [1.2.0] - 2020-09-15

- Rename package.json package name
- Fix htaccess middleware for Django 2
- Fix configuration options for givesome theme

## [1.1.0] - 2020-08-27

### Changed

- Make US and USD be the default country and currency

### Fixed

- Fix management command to use only the username as the key to return the admin user

### Added

- Add multivendor shipping checkout phase
- Add default permissions inside config.json file
- Add custom template to list grouped orders
- Add management commands to save and load project configurations and permissions

## [1.0.9] - 2020-08-10

- Add Django 2 support

## [1.0.8] - 2020-08-10

- Move enforcing stripe connect for vendors behind setting

## [1.0.7] - 2020-08-05

### Changed

- Add shuup-stripe-multivendor and remove shuup-stripe-connect-multivendor
- Bump several addons to latest version

### Removed

- Remove `shuup.front.saved_carts`

### Fixed

- Fix the enforcement middleware to consider Stripe connect even if vendor plans is disabled

### Added

- Add values for new shuup settings `SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION` and `SHUUP_ADMIN_ALLOW_HTML_IN_VENDOR_DESCRIPTION`.
- Add stop impersonate to permitted views
- Add timezone activating middleware

## [1.0.6] - 2020-07-27

- Theme: add render_navigation import to base.jinja

## [1.0.5] - 2020-06-11

- Bump definite theme to v2.1.5

## [1.0.4] - 2020-04-08

- Bump definite theme to v2.1.0

## [1.0.3] - 2020-04-08

### Added

- Add new middleware to redirect admin users when vendor plans are enabled

### Changed

- Bump `shuup-definite-theme` package to v2.0.5S

### Fixed

- Change browserlist to browserslist at package.json for future projects

## [1.0.2] - 2020-01-20

- Fix issue with givesome template setup. Fallback to `shuup-definite-theme`
  templates and introduce own template-dir for givesome theme

## [1.0.1] - 2020-01-09

### Added

- Givesome theme:

Givesome theme for your custom storefront. If you use this givesome
project for your implemention just rename the theme for your
convenience.

This theme is inherited from `shuup-definite-theme` v2.0.3 enabling you
option to add your own styles and Javascript in addition you can
override any template defined in `shuup-definite-theme`, `shuup.front` or
any other app defined in your project. Template dir is "templates/shuup_definite_theme"
as for `shuup-definite-theme` add all front related new or re-defining templates here.


## [1.0.0] - 2020-01-06

### Added

- Initial app
